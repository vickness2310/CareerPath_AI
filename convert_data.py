"""
convert_data.py
Run this ONCE to convert your 3 Kaggle CSV files into kaggle_data.json
Usage: python convert_data.py
"""
import pandas as pd
import json
import os

print("🔄 Converting Kaggle CSV files to JSON...")

# ── Load all 3 datasets ──
career_df = pd.read_csv('data/career_recommender.csv')
career_df.columns = ['name','gender','course','specialization','interests',
                     'skills','cgpa','certification','cert_title','working',
                     'job_title','masters']

salary_df = pd.read_csv('data/Salary_Data.csv')
salary_df.columns = ['age','gender','education','job_title','experience','salary']
salary_df = salary_df.dropna(subset=['salary','job_title'])

uni_df = pd.read_csv('data/world-universities.csv', header=None,
                     names=['country','name','website'])
malaysia_unis = uni_df[uni_df['country']=='MY'].reset_index(drop=True)

print(f"✅ Career surveys loaded:     {len(career_df):,} rows")
print(f"✅ Salary records loaded:     {len(salary_df):,} rows")
print(f"✅ Malaysian universities:    {len(malaysia_unis)} unis")

# ── Build salary lookup ──
salary_lookup = {}
for job, group in salary_df.groupby('job_title'):
    salary_lookup[job] = {
        'avg':   round(float(group['salary'].mean()) * 4.7 / 12),
        'min':   round(float(group['salary'].min())  * 4.7 / 12),
        'max':   round(float(group['salary'].max())  * 4.7 / 12),
        'count': int(len(group))
    }

# ── Interest → Career map ──
interest_map = {
    'coding':        ['Software Engineer','Software Developer','Data Analyst','Data Scientist','Web Developer'],
    'maths':         ['Data Analyst','Data Scientist','Financial Analyst','Accountant','Statistician'],
    'leadership':    ['Project Manager','Senior Manager','Director','Operations Manager','HR Manager'],
    'science':       ['Research Scientist','Senior Scientist','Biologist','Chemist','Lab Technician'],
    'design':        ['Graphic Designer','UX Designer','Product Designer','Creative Director'],
    'business':      ['Business Analyst','Marketing Manager','Sales Manager','Financial Analyst','Consultant'],
    'communication': ['Marketing Coordinator','HR Manager','Content Writer','Public Relations Manager'],
    'healthcare':    ['Doctor','Nurse','Pharmacist','Medical Assistant','Health Coach'],
    'engineering':   ['Mechanical Engineer','Civil Engineer','Electrical Engineer','Software Engineer'],
    'education':     ['Teacher','Training Manager','Academic Advisor','Curriculum Developer'],
    'environment':   ['Environmental Scientist','Sustainability Consultant','Ecologist','Geologist'],
    'law':           ['Lawyer','Legal Advisor','Compliance Officer','Paralegal']
}

# ── University details per career ──
uni_details = {
    'Software Engineer':   [
        {'name':'Universiti Malaya (UM)','location':'Kuala Lumpur','course':'Bachelor of Computer Science'},
        {'name':'Universiti Teknologi Malaysia (UTM)','location':'Johor Bahru','course':'Bachelor of Software Engineering'},
        {'name':'Multimedia University (MMU)','location':'Cyberjaya, Selangor','course':'Bachelor of Computer Science'}],
    'Data Analyst':        [
        {'name':'Universiti Malaya (UM)','location':'Kuala Lumpur','course':'Bachelor of Data Science'},
        {'name':'Universiti Kebangsaan Malaysia (UKM)','location':'Bangi, Selangor','course':'Bachelor of Information Technology'},
        {'name':'Asia Pacific University (APU)','location':'Kuala Lumpur','course':'Bachelor of Data Analytics'}],
    'Data Scientist':      [
        {'name':'Universiti Malaya (UM)','location':'Kuala Lumpur','course':'Bachelor of Data Science'},
        {'name':'Universiti Teknologi Malaysia (UTM)','location':'Johor Bahru','course':'Bachelor of Computer Science'},
        {'name':'Sunway University','location':'Subang Jaya, Selangor','course':'Bachelor of Data Science'}],
    'Business Analyst':    [
        {'name':'Universiti Malaya (UM)','location':'Kuala Lumpur','course':'Bachelor of Business Administration'},
        {'name':'Universiti Utara Malaysia (UUM)','location':'Sintok, Kedah','course':'Bachelor of Business Analytics'},
        {'name':"Taylor's University",'location':'Subang Jaya, Selangor','course':'Bachelor of Business'}],
    'Financial Analyst':   [
        {'name':'Universiti Malaya (UM)','location':'Kuala Lumpur','course':'Bachelor of Finance'},
        {'name':'UTAR','location':'Kampar, Perak','course':'Bachelor of Accounting'},
        {'name':'Universiti Utara Malaysia (UUM)','location':'Sintok, Kedah','course':'Bachelor of Finance'}],
    'Doctor':              [
        {'name':'Universiti Malaya (UM)','location':'Kuala Lumpur','course':'Bachelor of Medicine (MBBS)'},
        {'name':'Universiti Kebangsaan Malaysia (UKM)','location':'Bangi, Selangor','course':'Bachelor of Medicine (MBBS)'},
        {'name':'International Medical University (IMU)','location':'Kuala Lumpur','course':'Bachelor of Medicine (MBBS)'}],
    'Nurse':               [
        {'name':'Universiti Kebangsaan Malaysia (UKM)','location':'Bangi, Selangor','course':'Bachelor of Nursing'},
        {'name':'AIMST University','location':'Bedong, Kedah','course':'Bachelor of Nursing Science'},
        {'name':'Universiti Malaya (UM)','location':'Kuala Lumpur','course':'Bachelor of Nursing'}],
    'Pharmacist':          [
        {'name':'Universiti Malaya (UM)','location':'Kuala Lumpur','course':'Bachelor of Pharmacy'},
        {'name':'Universiti Sains Malaysia (USM)','location':'Penang','course':'Bachelor of Pharmacy'},
        {'name':'AIMST University','location':'Bedong, Kedah','course':'Bachelor of Pharmacy'}],
    'Mechanical Engineer': [
        {'name':'Universiti Teknologi Malaysia (UTM)','location':'Johor Bahru','course':'Bachelor of Mechanical Engineering'},
        {'name':'Universiti Malaya (UM)','location':'Kuala Lumpur','course':'Bachelor of Mechanical Engineering'},
        {'name':'Universiti Tenaga Nasional (UNITEN)','location':'Kajang, Selangor','course':'Bachelor of Mechanical Engineering'}],
    'Civil Engineer':      [
        {'name':'Universiti Teknologi Malaysia (UTM)','location':'Johor Bahru','course':'Bachelor of Civil Engineering'},
        {'name':'Universiti Malaya (UM)','location':'Kuala Lumpur','course':'Bachelor of Civil Engineering'},
        {'name':'Universiti Putra Malaysia (UPM)','location':'Serdang, Selangor','course':'Bachelor of Civil Engineering'}],
    'Lawyer':              [
        {'name':'Universiti Malaya (UM)','location':'Kuala Lumpur','course':'Bachelor of Laws (LLB)'},
        {'name':'International Islamic University Malaysia (IIUM)','location':'Gombak, Selangor','course':'Bachelor of Laws (LLB)'},
        {'name':'Universiti Kebangsaan Malaysia (UKM)','location':'Bangi, Selangor','course':'Bachelor of Laws (LLB)'}],
    'Teacher':             [
        {'name':'Universiti Pendidikan Sultan Idris (UPSI)','location':'Tanjung Malim, Perak','course':'Bachelor of Education'},
        {'name':'Universiti Kebangsaan Malaysia (UKM)','location':'Bangi, Selangor','course':'Bachelor of Education'},
        {'name':'Universiti Malaya (UM)','location':'Kuala Lumpur','course':'Bachelor of Education'}],
    'Graphic Designer':    [
        {'name':'Multimedia University (MMU)','location':'Cyberjaya, Selangor','course':'Bachelor of Creative Multimedia'},
        {'name':"Taylor's University",'location':'Subang Jaya, Selangor','course':'Bachelor of Design'},
        {'name':'The One Academy','location':'Subang Jaya, Selangor','course':'Diploma in Graphic Design'}],
    'HR Manager':          [
        {'name':'Universiti Malaya (UM)','location':'Kuala Lumpur','course':'Bachelor of Human Resource Management'},
        {'name':'Universiti Utara Malaysia (UUM)','location':'Sintok, Kedah','course':'Bachelor of Human Resource Management'},
        {'name':'Universiti Putra Malaysia (UPM)','location':'Serdang, Selangor','course':'Bachelor of Human Resource Development'}],
}

default_unis = [
    {'name':'Universiti Malaya (UM)','location':'Kuala Lumpur','course':'Bachelor of Science'},
    {'name':'Universiti Kebangsaan Malaysia (UKM)','location':'Bangi, Selangor','course':'Bachelor of Science'},
    {'name':'Universiti Teknologi Malaysia (UTM)','location':'Johor Bahru','course':'Bachelor of Technology'}
]

# ── PTPTN info per career ──
ptptn_info = {
    'Software Engineer':   {'total':45000,'ptptn':40500,'monthly':225,'years':15,'duration':'4 years'},
    'Software Developer':  {'total':40000,'ptptn':36000,'monthly':200,'years':15,'duration':'4 years'},
    'Data Analyst':        {'total':38000,'ptptn':34200,'monthly':190,'years':15,'duration':'3 years'},
    'Data Scientist':      {'total':48000,'ptptn':43200,'monthly':240,'years':15,'duration':'4 years'},
    'Business Analyst':    {'total':35000,'ptptn':31500,'monthly':175,'years':15,'duration':'3 years'},
    'Financial Analyst':   {'total':36000,'ptptn':32400,'monthly':180,'years':15,'duration':'3 years'},
    'Marketing Manager':   {'total':32000,'ptptn':28800,'monthly':160,'years':15,'duration':'3 years'},
    'Project Manager':     {'total':34000,'ptptn':30600,'monthly':170,'years':15,'duration':'3 years'},
    'Doctor':              {'total':180000,'ptptn':162000,'monthly':900,'years':15,'duration':'5 years'},
    'Nurse':               {'total':25000,'ptptn':22500,'monthly':125,'years':15,'duration':'3 years'},
    'Pharmacist':          {'total':80000,'ptptn':72000,'monthly':400,'years':15,'duration':'4 years'},
    'Mechanical Engineer': {'total':42000,'ptptn':37800,'monthly':210,'years':15,'duration':'4 years'},
    'Civil Engineer':      {'total':40000,'ptptn':36000,'monthly':200,'years':15,'duration':'4 years'},
    'Electrical Engineer': {'total':43000,'ptptn':38700,'monthly':215,'years':15,'duration':'4 years'},
    'Lawyer':              {'total':55000,'ptptn':49500,'monthly':275,'years':15,'duration':'4 years'},
    'Teacher':             {'total':28000,'ptptn':25200,'monthly':140,'years':15,'duration':'4 years'},
    'Graphic Designer':    {'total':30000,'ptptn':27000,'monthly':150,'years':15,'duration':'3 years'},
    'UX Designer':         {'total':35000,'ptptn':31500,'monthly':175,'years':15,'duration':'3 years'},
    'HR Manager':          {'total':30000,'ptptn':27000,'monthly':150,'years':15,'duration':'3 years'},
    'Research Scientist':  {'total':45000,'ptptn':40500,'monthly':225,'years':15,'duration':'4 years'},
}
default_ptptn = {'total':40000,'ptptn':36000,'monthly':200,'years':15,'duration':'4 years'}

# ── Combine everything ──
output = {
    'salary_lookup': salary_lookup,
    'interest_map':  interest_map,
    'uni_details':   uni_details,
    'default_unis':  default_unis,
    'ptptn_info':    ptptn_info,
    'default_ptptn': default_ptptn,
    'stats': {
        'total_salary_records': int(len(salary_df)),
        'total_career_surveys': int(len(career_df)),
        'total_malaysian_unis': int(len(malaysia_unis))
    }
}

os.makedirs('data', exist_ok=True)
with open('data/kaggle_data.json', 'w') as f:
    json.dump(output, f, indent=2)

size = os.path.getsize('data/kaggle_data.json') / 1024
print(f"\n✅ kaggle_data.json created! ({size:.1f} KB)")
print(f"   Salary job titles:    {len(salary_lookup)}")
print(f"   Career interest maps: {len(interest_map)}")
print(f"   University mappings:  {len(uni_details)} careers")
print(f"   PTPTN entries:        {len(ptptn_info)} careers")
print("\n🎉 Done! Now just open index.html in your browser!")
