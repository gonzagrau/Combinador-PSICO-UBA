# PsiComb: A class schedule maker for the UBA Faculty of Psychology
When your school has a large collection of class sections for every subject, and you plan to take more than one subject every semester, finding a valid non-overlapping combination of section for every subject can be a struggle. Besides, the course information available online may be messy, which makes this process even harder. Enter: PsiComb, an automatic class scheduler that finds every possible section combination for the subjects of your choice.

## Step-by-step guide

### Step 1: input your chosen subjects by providing the URL to its course information page
![psicomb_tut_1](https://github.com/gonzagrau/Combinador-PSICO-UBA/assets/107513203/ec78cfc0-04fb-42c8-9fee-994c94c1a212)


### Step 2: choose your favorite sections (comissions) for each subjects
![psicomb_tut_2](https://github.com/gonzagrau/Combinador-PSICO-UBA/assets/107513203/3929b767-3e95-4809-a6e2-6890657b1303)


### Step 3: Combine! all possible results are display onscreen, with a more detailed view available on Excel
![psicomb_tut_3](https://github.com/gonzagrau/Combinador-PSICO-UBA/assets/107513203/b35d00e0-46db-45f5-9300-75a800cd463b)


## What PsiComb does
PsiComb automatically parses the course information directly from the online campus, so that you don't have to deal with "building" your section by merging theory, seminaries, and practical classes. In other words, you go from this...
![image](https://github.com/gonzagrau/Combinador-PSICO-UBA/assets/107513203/66accbd1-25aa-4372-a989-08bce31455d2)

... to this
<p align="center">
 <img src="https://github.com/gonzagrau/Combinador-PSICO-UBA/assets/107513203/9284f57b-0708-43ec-b087-8280da0e1927)"/>
</p>

This allows the user to easily identify feasible options for each subjects, which can then be combined with other sections from different courses. Then, after making a choice and clicking on "Calcular combinaciones", a tabview with all non-overlapping combinations posssible shows up. 

***NOTE: these are not the actual weekly timetables, but only an approximation that is easier to read. The full, completely accurate schedules are saved to the Excel file***

Other cool features include:
<ul>
  <li>User-friendly GUI, built with CustomTKinter</li>
  <li>'Psi' button with a link to the web campus</li>
  <li>Add/delete subject buttons</li>
  <li>Go-back buttons, to save progress</li>
  <li>Color-coded schedule display</li>
  <li>Light/dark mode switch</li>
  <li>Github repository link</li>
</ul>


## Who can use PsiComb?
This combiner was created exclusively for the UBA Faculty of Psychology. It is free and open source, and relies exclusively on information that is freely available online.

## Some code snippets

### Internal representation of subjects, class sections (comissions), and weekly hours
The irreductible unit of a subject section is no more than a time interval within a specific weekday, with an assigned proffessor and sometimes an observation. The CourseBlock class abstracts this concept:

```python
class CourseBlock(object):
    """
    A course block represents a grouping of a weekday and a time interval,
    delimited by the start time and the end time
    """
    def __init__(self, weekday: str, start_time: time, end_time: time, teacher: str='', observation: str=''):
        for x in start_time, end_time:
            assert isinstance(x, time), 'Invalid start or end time'
        assert start_time < end_time, 'Start time should be smaller than endtime'
        weekday = weekday.upper()
        assert weekday in weekdays_list, 'Invalid weekday'
        self.weekday = weekday
        self.start_time = start_time
        self.end_time = end_time
        self.teacher = teacher
        self.observation = observation

    def __eq__(self, other):
        return self.weekday == other.weekday and self.start_time == other.start_time and self.end_time == other.end_time

    def __str__(self):
        return f"{self.weekday}\n{self.start_time.isoformat(timespec='minutes')} - " \
                + f"{self.end_time.isoformat(timespec='minutes')}\n" \
                + f"Prof.: {self.teacher}" \
                + f"\nObser.: {self.observation}"*int(bool(len(self.observation)))

    def collides_with(self, other):
        if self.weekday != other.weekday:
            return False
        return other.start_time <= self.start_time < other.end_time \
               or self.start_time <= other.start_time < self.end_time
```
Note that the collided_with method indicates whether a course block overlaps with another one, which is precisely what we want to avoid when finding a combination.

Then, comissions (class sections) are no more than a named collection of course blocks:

```python
class Comission(object):
    """
    A comission is a grouping of course blocks, with a unique identifier
    """
    def __init__(self, identifyer: str | int, block_list: List[CourseBlock] = None):
        assert type(identifyer) == str, 'Invalid comission id'
        self.identifyer = identifyer
        if block_list is None:
            self.block_list = []
        else:
            self.block_list = block_list
        self._sel = True

    def add_course_block(self, c_block: CourseBlock):
        self.block_list.append(c_block)

    def __str__(self):
        return f"Comision {self.identifyer}\n" + self.blocks_str()

    def blocks_str(self):
        return '\n'.join([f"{str(block)}" for block in self.block_list])

    def collides_with(self, other):
        for sblock in self.block_list:
            for oblock in other.block_list:
                if sblock.collides_with(oblock):
                    return True
        return False

    def select(self):
        self._sel = True

    def deselect(self):
        self._sel = False

    def is_selected(self):
        return self._sel
```
The selection/deselection methods, although irrelevant for the internal representation, are useful for the GUI implementation (these methods are called when the checkboxes for each comission are acted upon).

Finally, a subject is a named collection of comissions, and a combination is simply a list of comissions from different subjects

```python
class Subject(object):
    """
    A subject has a name and a list of comissions
    """
    def __init__(self, name: str, comission_list: List[Comission] = None):
        self.name = name
        if comission_list is None:
            self.comission_list = []
        else:
            self.comission_list = comission_list

    def __str__(self):
        return f"{len(self.name)*'_'}\n{self.name}\n{len(self.name)*'_'}\n" + \
               ''.join([f"{str(comission)}\n" for comission in self.comission_list])

    def append_comission(self, comission: Comission):
        self.comission_list.append(comission)

    def get_selected_comissions(self):
        return [com for com in self.comission_list if com.is_selected()]
```

```python
class Combination(List[Comission]):
    """
    A combination is simply a list of comissionissions
    """
    def is_valid(self):
        for i in range(len(self)):
            for j in range(i+1, len(self)):
                if self[i].collides_with(self[j]):
                    return False
        return True

    def copy(self):
    # overrides copy to return a Combination object
        new = Combination()
        for el in self:
            new.append(el)
        return new
    def __str__(self):
        return '[' + ', '.join([str(comission.identifyer) for comission in self]) + ']'
```

### Combination algorithm
The combining function makes use of all these objects, and recursively searchs for all valid collections of comissions

```python
def find_combinations(subjects: List[Subject], current_combination=None, index: int = 0) -> List[Combination]:
    """
    :param subjects: list of Subject objects
    :param current_combination: Combination object (defaults to newly created Combination object)
    :param index: index to the current subject at the subjects list
    :return: comb_list, a list of all possible combinations
    """
    if current_combination is None:
        current_combination = Combination()
    comb_list = []
    current_subject = subjects[index]

    for comission in current_subject.get_selected_comissions():
        # append to a copy of the ongoing combination in case the current comission collides with it
        new_combination = current_combination.copy()
        new_combination.append(comission)
        if not new_combination.is_valid():
            continue
        if index == len(subjects) - 1: # if the recursion reached the last subject, save the combination
            comb_list.append(new_combination)
        else: # move on to the next subject
            new_comb_list = find_combinations(subjects, new_combination, index+1)
            comb_list = comb_list + new_comb_list

    return comb_list
```

### Schedules
Once a valid combination is found, a pandas dataframe is used to display it. A color code is randomly assigned to each unique comission, by choosing from the matplotlib.mcolors module

```python
class Schedule(pd.DataFrame):
    color_dict = {}
    colors_list = list(mcolors.TABLEAU_COLORS.values())
    
    def __init__(self, freq : str='15T'):
        time_series = pd.date_range(start='07:00', end='23:00', freq=freq).time
        super().__init__('', index=time_series, columns= list(combiner.weekdays_list))

    def add_course_block(self, course_block: combiner.CourseBlock, repr_str: str) -> None:
        self.loc[course_block.start_time : course_block.end_time, course_block.weekday].iloc[:-1] = repr_str
        if repr_str not in self.color_dict.keys():
            if len(self.colors_list) == 0: # reset colors if we run out of them
                self.colors_list = list(mcolors.TABLEAU_COLORS.values())
            chosen_color = random.choice(self.colors_list)
            self.colors_list.remove(chosen_color)
            self.color_dict[repr_str] = chosen_color

    def add_combination(self, subjects: List[combiner.Subject], combination: combiner.Combination) -> None:
        for subject, comission in zip(subjects, combination):
            sub_name = subject.name
            for block in comission.block_list:
                self.add_course_block(block, f"{sub_name} {comission.identifyer}")

    def apply_format(self):
        # format index
        self.index = self.index.map(lambda t: t.strftime('%H:%M'))
        # color inner cells first
        def color_func(value):
            return f'background-color: {self.color_dict.get(value, "white")}; border: 1px solid grey;'
        return self.style.applymap(color_func)
```

## Upcoming developments
Currently, I'm working on fully automating the web scrapping process, so that the user doesn't even have to manually input the URLs for each subject. The idea would be to select from a list of all available subjects, which can automatically be extracted from the website. This has already been achieved, but I am yet to add it to the GUI in a user-friendly way (which may imply using a whole different front-end framework)

## Special thanks to...
Agus <3
