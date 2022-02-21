from xml.etree import ElementTree

@login_required
@permission_required("college.add_timetable", raise_exception=True)
@permission_required("college.change_timetable", raise_exception=True)
@permission_required("college.delete_timetable", raise_exception=True)
@permission_required("college.view_timetable", raise_exception=True)
def Create_TimeTable(request):
    xml_TimeTable=[]
    xml_all_roots=[]
    xml_card_element=[]
    xml_lesson_element=[]
    xml_class_element=[]
    xml_subject_element=[]
    xml_daysdef_element=[]
    xml_period_element=[]
    if request.method == 'POST':
        if request.FILES.get('xml_file'):
            xml_file_name = request.POST.get('xml_file_name')
            xml_file = request.FILES['xml_file']
            try:
                os.remove('XML_Files/Time_Table.xml')
            except:
                pass
            fs = FileSystemStorage(location='XML_Files/') 
            filename = fs.save('Time_Table.xml', xml_file)
      
        xml_TimeTable = ElementTree.parse('XML_Files/Time_Table.xml') # all element of xml file has been read by element tree
        xml_all_roots = xml_TimeTable.getroot() # all the roots example tages has been read
        xml_period_element = xml_all_roots[0].findall('period') # period element has been read for course time
        xml_daysdef_element = xml_all_roots[1].findall('daysdef') # days element has been read for course day
        xml_subject_element = xml_all_roots[4].findall('subject') # subject element has been read for course name
        xml_class_element = xml_all_roots[9].findall('class') # class element has been read for class name
        xml_lesson_element = xml_all_roots[13].findall('lesson') # lesson element has been read, it includes class id and subject id for class name and subject name
        xml_card_element = xml_all_roots[14].findall('card')  
        TimeTable.objects.filter(semester=get_last_semester()).delete()
      
    Time_Table_Data = []
    for index, card in enumerate(xml_card_element): # main loop include all card element with period, days and lesson id. card id will be correlate with lesson id to extract class and subject id
        lesson_id = card.attrib['lessonid'] # from card element lessonid attribute has been read for searching conected class and subject
        period_id = card.attrib['period'] # from card element period attribute has been read for course time
        days_id = card.attrib['days'] # from card element days attribute has been read for course day
        Time_Table_Data.append([]) # (2d List) array with in array to append new array for each class 
        for lesson in xml_lesson_element:   # secondary loop to search above mention lessonid   
            if lesson_id == lesson.attrib['id']: # if lesson id is matched with the id of lesson element
                class_id = lesson.attrib['classids'] # respective class id of above searched lessonid has been read 
                subject_id = lesson.attrib['subjectid'] # respective subject id of above searched lesson id has been read 
                if len(class_id) > 16: # if class id is more than 1, note: length of single class id is 16 character 
                    class_id_list = lesson.attrib['classids'].split(',') # splitting of multiple class id to control class id one by one.
                    for id_class in class_id_list: # loop for multiple class id in order to check class name one by one
                        for clas in xml_class_element:
                            if id_class == clas.attrib['id']:  # if class id is matched with the ids of class 
                                Time_Table_Data[index].append(clas.attrib['name'])  # from class element by corelating class id, class name has been read and appended to the array according to the index.
                        for subject in xml_subject_element:
                            if subject_id == subject.attrib['id']: # if subject id is matched with the ids of subject element
                                Time_Table_Data[index].append(subject.attrib['name'])  # from subject element by corelating subject id, subject name has been read and appended to the array according to the index.
                                Time_Table_Data[index].append(subject.attrib['short']) # from subject element by corelating subject id, course code has been read and appended to the array according to the index.
                        for period in xml_period_element:
                            if period_id == period.attrib['period']: # if period id is matched with the ids of period element for course time
                                Time_Table_Data[index].append(period.attrib['period']) # from period element by corelating subject id, subject name has been read and appended to the array according to the index.                      
                        for day in xml_daysdef_element:
                            if days_id == day.attrib['days']: # if days id is matched with the ids of days element for course day
                                Time_Table_Data[index].append(day.attrib['name'])   # from days element by corelating day id, day has been read and appended to the array according to the index.                                            
                elif len(class_id) == 0: # if there is no class id , same action is repeated
                    Time_Table_Data[index].append('0A')# random class has been append in order to prevent list out of range error
                    for subject in xml_subject_element:
                        if subject_id == subject.attrib['id']:
                            Time_Table_Data[index].append(subject.attrib['name'])
                            Time_Table_Data[index].append(subject.attrib['short'])
                    for period in xml_period_element:
                        if period_id == period.attrib['period']:
                            Time_Table_Data[index].append(period.attrib['period'])
                    for day in xml_daysdef_element:
                        if days_id == day.attrib['days']:
                            Time_Table_Data[index].append(day.attrib['name'])   
                else: # if there is only one class, and same action is repeated
                    for clas in xml_class_element:
                        if class_id == clas.attrib['id']:
                            Time_Table_Data[index].append(clas.attrib['name'])
                    for subject in xml_subject_element:
                        if subject_id == subject.attrib['id']:
                            Time_Table_Data[index].append(subject.attrib['name'])
                            Time_Table_Data[index].append(subject.attrib['short'])
                            Courses.objects.filter(semester=get_last_semester(),course_code=subject.attrib['short'])
                    for period in xml_period_element:
                        if period_id == period.attrib['period']:
                            Time_Table_Data[index].append(period.attrib['period'])
                    for day in xml_daysdef_element:
                        if days_id == day.attrib['days']:
                            Time_Table_Data[index].append(day.attrib['name'])
    for multiple_class_id in Time_Table_Data: # for multiple class id array length is greater then 5 so, to extract other class ids data if check on main array to retrive data. 
        count = 5 # second class id data starts from 5th index of list
        if len(multiple_class_id) > 5:
            for class_ids in multiple_class_id:
                if len(multiple_class_id) > count:
                    Time_Table_Data.append(multiple_class_id[count:count+5]) # second class id data append for example from 5 to 10, 11 to 15 and  onwards 
                count += 5
    course_day = 0
    Lesson_Hour = None
    for Data in Time_Table_Data: 
        if translation.get_language()=='en' :
            if Data[4]== 'Pazartesi': # data[4] = days
                Data[4] = 'Monday'
            elif Data[4]== 'Salı':
                Data[4] = 'Tuesday' 
            elif Data[4]== 'Çarşamba':
                Data[4] = 'Wednesday' 
            elif Data[4]== 'Perşembe':
                Data[4] = 'Thursday'  
            elif Data[4]== 'Cuma':
                Data[4] = 'Friday'    
        for days in COURSE_DAYS: 
            if Data[4] == days[1]:    
                course_day = days[0]                        
    # data[0] is class name, in order to check the class year 6,7,8,9,10,11,12 further classification has benn done. data[0][0] contain first character of class. 
        if Data[0][0] == '9' or (Data[0][0] =='1' and Data[0][1] =='0') or(Data[0][0] =='1' and Data[0][1] =='1') or (Data[0][0] =='1' and Data[0][1] =='2'): 
            if Data[0][0] == '9': # Data[0][0] if class year is 9 
                timeTable_class_year= Data[0][0] # Data[0][0] is class year 
                timaTable_class_name = Data[0][1]# Data[0][0] is class name 
                timeTable_class_branch = Data[0][3:] # Data[0][0] is class branch
            else:
                timeTable_class_year= Data[0][0:2] # Data[0][0] class year is 10,11,12
                timaTable_class_name = Data[0][2] # Data[0][2] is class name
                timeTable_class_branch = Data[0][4:] # Data[0][4] is class branch
            class_object = Classes.objects.filter(class_year = timeTable_class_year,class_name=timaTable_class_name,class_branch=timeTable_class_branch).first()
            course_object = Courses.objects.filter(class_year = timeTable_class_year,class_branch = timeTable_class_branch, course_code= Data[2]).first()
        elif Data[0][0] == '6' or Data[0][0] == '7' or Data[0][0] == '8': # Data[0][0] class year is 6,7,8
            timeTable_class_year = Data[0][0]
            timaTable_class_name = Data[0][1]
            class_object = Classes.objects.filter(class_year = timeTable_class_year,class_name=timaTable_class_name).first()
            course_object = Courses.objects.filter(class_year = timeTable_class_year, course_code= Data[2]).first()

        Lesson_hour = LessonHours.objects.filter(lessonhour = Data[3]).first()
        if course_object: # only available class time table will be inserted else will not be added. 
            TimeTable.objects.get_or_create(semester=get_last_semester(),course_class =class_object,course =course_object,course_hour= Lesson_hour,course_day=course_day)[0]
        else:
            pass
    
    Class_List = Classes.objects.filter(semester=get_last_semester(),class_year__gt=1)
    Lesson_Hours = LessonHours.objects.all().order_by('lessonhour')
    class_uuid=request.GET.get('class_uuid')
    
    if request.method == 'POST':
        Class_Object = Classes.objects.filter(uuid = request.POST.get('class_uuid')).first()
        timetable_list = [request.POST.getlist('Timetable_0'),request.POST.getlist('Timetable_1'),request.POST.getlist('Timetable_2'),request.POST.getlist('Timetable_3'),request.POST.getlist('Timetable_4'),request.POST.getlist('Timetable_5'),request.POST.getlist('Timetable_6'),request.POST.getlist('Timetable_7'),request.POST.getlist('Timetable_8')]

        for index, course_hour in enumerate(Lesson_Hours):
            for i, Timetable_Course_uuid in enumerate(timetable_list[index]):
                if not Timetable_Course_uuid == '-':
                    course_object = Courses.objects.filter(uuid = Timetable_Course_uuid).first()
                    if TimeTable.objects.filter(semester=get_last_semester(),course_class = Class_Object,course_hour = course_hour,course_day = COURSE_DAYS[i][0]).exists():
                        TimeTable.objects.filter(semester=get_last_semester(),course_class = Class_Object,course_hour = course_hour,course_day = COURSE_DAYS[i][0]).update(course = course_object)
                    else:
                        Timetable_1 = TimeTable.objects.create(semester=get_last_semester(),course_class = Class_Object,course =course_object,course_hour = course_hour,course_day = COURSE_DAYS[i][0])
                else:
                    TimeTable.objects.filter(semester=get_last_semester(),course_class = Class_Object,course_hour = course_hour,course_day = COURSE_DAYS[i][0]).delete()

    if class_uuid:
        Class_Object = Classes.objects.filter(uuid=class_uuid).first()
        Course_object_List = Courses.objects.filter(semester=get_last_semester(),class_year=Class_Object.class_year)
        timetable_objects = TimeTable.objects.filter(course_class=Class_Object).order_by('course_day','course_hour')
        
        timetable_data = []
        if timetable_objects:
            for lessonhour in Lesson_Hours:
                ptesi = TimeTable.objects.filter(course_class__class_year = Class_Object.class_year,course_class__class_name = Class_Object.class_name,course_hour = lessonhour,course_day = 1).first() or '-'
                sali = TimeTable.objects.filter(course_class__class_year = Class_Object.class_year,course_class__class_name = Class_Object.class_name,course_hour = lessonhour,course_day = 2).first() or '-'
                crs = TimeTable.objects.filter(course_class__class_year = Class_Object.class_year,course_class__class_name = Class_Object.class_name,course_hour = lessonhour,course_day = 3).first() or '-'
                prs = TimeTable.objects.filter(course_class__class_year = Class_Object.class_year,course_class__class_name = Class_Object.class_name,course_hour = lessonhour,course_day = 4).first() or '-'
                cuma = TimeTable.objects.filter(course_class__class_year = Class_Object.class_year,course_class__class_name = Class_Object.class_name,course_hour = lessonhour,course_day = 5).first() or '-'
                timetable_data.append([lessonhour,ptesi,sali,crs,prs,cuma])
        return render(request, 'Create-TimeTable.html', {'Course_object_List':Course_object_List,'Class_List':Class_List,'Class_Object':Class_Object,'timetable_data': timetable_data,'Time_Table_Data':Time_Table_Data})
    else:
        return render(request, 'Create-TimeTable.html', {'Class_List':Class_List,'Time_Table_Data':Time_Table_Data})