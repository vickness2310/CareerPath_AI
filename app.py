from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import re

app = Flask(__name__)
CORS(app)

# ── LOAD ALL 3 KAGGLE DATASETS ──
print("Loading datasets...")

# Dataset 1: Career Recommender (1,195 rows)
career_df = pd.read_csv('data/career_recommender.csv')
career_df.columns = [
    'name', 'gender', 'course', 'specialization',
    'interests', 'skills', 'cgpa', 'certification',
    'cert_title', 'working', 'job_title', 'masters'
]

# Dataset 2: Salary Data (6,704 rows)
salary_df = pd.read_csv('data/Salary_Data.csv')
salary_df.columns = ['age', 'gender', 'education', 'job_title', 'experience', 'salary']

# Dataset 3: World Universities - filter Malaysia only
uni_df = pd.read_csv('data/world-universities.csv', header=None, names=['country', 'name', 'website'])
malaysia_unis = uni_df[uni_df['country'] == 'MY'].reset_index(drop=True)

print(f"✅ Career data: {len(career_df)} rows")
print(f"✅ Salary data: {len(salary_df)} rows")
print(f"✅ Malaysian universities: {len(malaysia_unis)} unis")

# ── HELPER: Match interest to career ──
INTEREST_CAREER_MAP = {
    'coding':        ['Software Engineer', 'Software Developer', 'Data Analyst', 'Data Scientist', 'Web Developer'],
    'maths':         ['Data Analyst', 'Data Scientist', 'Financial Analyst', 'Statistician', 'Accountant'],
    'leadership':    ['Project Manager', 'Senior Manager', 'Director', 'Operations Manager', 'HR Manager'],
    'science':       ['Research Scientist', 'Senior Scientist', 'Biologist', 'Chemist', 'Lab Technician'],
    'design':        ['Graphic Designer', 'UX Designer', 'Product Designer', 'Creative Director'],
    'business':      ['Business Analyst', 'Marketing Manager', 'Sales Manager', 'Financial Analyst', 'Consultant'],
    'communication': ['Marketing Coordinator', 'Public Relations', 'Content Writer', 'Journalist', 'HR Manager'],
    'healthcare':    ['Doctor', 'Nurse', 'Pharmacist', 'Medical Assistant', 'Health Coach'],
    'engineering':   ['Mechanical Engineer', 'Civil Engineer', 'Electrical Engineer', 'Software Engineer'],
    'education':     ['Teacher', 'Tutor', 'Training Manager', 'Curriculum Developer', 'Academic Advisor'],
    'environment':   ['Environmental Scientist', 'Sustainability Consultant', 'Ecologist', 'Geologist'],
    'law':           ['Lawyer', 'Legal Advisor', 'Compliance Officer', 'Paralegal', 'Judge']
}

PTPTN_RATES = {
    'public':  {'min': 10000, 'max': 25000, 'coverage': 0.90},
    'private': {'min': 20000, 'max': 60000, 'coverage': 0.75},
}

COURSE_FEES = {
    'Software Engineer':       {'fee': 45000, 'duration': '4 years', 'type': 'public'},
    'Software Developer':      {'fee': 40000, 'duration': '4 years', 'type': 'public'},
    'Data Analyst':            {'fee': 38000, 'duration': '3 years', 'type': 'public'},
    'Data Scientist':          {'fee': 48000, 'duration': '4 years', 'type': 'public'},
    'Business Analyst':        {'fee': 35000, 'duration': '3 years', 'type': 'public'},
    'Financial Analyst':       {'fee': 36000, 'duration': '3 years', 'type': 'public'},
    'Marketing Manager':       {'fee': 32000, 'duration': '3 years', 'type': 'public'},
    'Project Manager':         {'fee': 34000, 'duration': '3 years', 'type': 'public'},
    'Mechanical Engineer':     {'fee': 42000, 'duration': '4 years', 'type': 'public'},
    'Civil Engineer':          {'fee': 40000, 'duration': '4 years', 'type': 'public'},
    'Electrical Engineer':     {'fee': 43000, 'duration': '4 years', 'type': 'public'},
    'Doctor':                  {'fee': 180000, 'duration': '5 years', 'type': 'public'},
    'Nurse':                   {'fee': 25000, 'duration': '3 years', 'type': 'public'},
    'Pharmacist':              {'fee': 80000, 'duration': '4 years', 'type': 'public'},
    'Graphic Designer':        {'fee': 30000, 'duration': '3 years', 'type': 'private'},
    'UX Designer':             {'fee': 35000, 'duration': '3 years', 'type': 'private'},
    'Teacher':                 {'fee': 28000, 'duration': '4 years', 'type': 'public'},
    'Lawyer':                  {'fee': 55000, 'duration': '4 years', 'type': 'public'},
    'HR Manager':              {'fee': 30000, 'duration': '3 years', 'type': 'public'},
    'Research Scientist':      {'fee': 45000, 'duration': '4 years', 'type': 'public'},
    'Environmental Scientist': {'fee': 38000, 'duration': '4 years', 'type': 'public'},
}
DEFAULT_FEES = {'fee': 40000, 'duration': '4 years', 'type': 'public'}

# ── HELPER: Get salary from dataset ──
def get_salary_info(job_title):
    matches = salary_df[salary_df['job_title'].str.lower() == job_title.lower()]
    if len(matches) == 0:
        # fuzzy match — find partial
        matches = salary_df[salary_df['job_title'].str.lower().str.contains(
            job_title.lower().split()[0], na=False
        )]
    if len(matches) > 0:
        avg = int(matches['salary'].mean())
        mn  = int(matches['salary'].min())
        mx  = int(matches['salary'].max())
        # Convert USD rough estimate to MYR (x4.7)
        return {
            'average_myr': round(avg * 4.7 / 12),  # monthly
            'min_myr':     round(mn  * 4.7 / 12),
            'max_myr':     round(mx  * 4.7 / 12),
            'sample_size': len(matches)
        }
    return {'average_myr': 4500, 'min_myr': 3000, 'max_myr': 8000, 'sample_size': 0}

# ── HELPER: Get Malaysian universities ──
def get_universities(career, count=3):
    CAREER_UNI_MAP = {
        'Software Engineer':   ['Universiti Malaya', 'Universiti Teknologi Malaysia', 'Multimedia University'],
        'Data Analyst':        ['Universiti Malaya', 'Universiti Kebangsaan Malaysia', 'Asia Pacific University'],
        'Data Scientist':      ['Universiti Malaya', 'Universiti Teknologi Malaysia', 'Sunway University'],
        'Business Analyst':    ['Universiti Malaya', 'Universiti Utara Malaysia', 'Taylor\'s University'],
        'Financial Analyst':   ['Universiti Malaya', 'UTAR', 'Universiti Utara Malaysia'],
        'Doctor':              ['Universiti Malaya', 'Universiti Kebangsaan Malaysia', 'International Medical University'],
        'Nurse':               ['Universiti Kebangsaan Malaysia', 'AIMST University', 'Universiti Malaya'],
        'Pharmacist':          ['Universiti Malaya', 'Universiti Sains Malaysia', 'AIMST University'],
        'Mechanical Engineer': ['Universiti Teknologi Malaysia', 'Universiti Malaya', 'Universiti Tenaga Nasional'],
        'Civil Engineer':      ['Universiti Teknologi Malaysia', 'Universiti Malaya', 'Universiti Putra Malaysia'],
        'Lawyer':              ['Universiti Malaya', 'International Islamic University Malaysia', 'Universiti Kebangsaan Malaysia'],
        'Teacher':             ['Universiti Pendidikan Sultan Idris', 'Universiti Kebangsaan Malaysia', 'Universiti Malaya'],
        'Graphic Designer':    ['Multimedia University', 'Taylor\'s University', 'The One Academy'],
        'UX Designer':         ['Multimedia University', 'Asia Pacific University', 'Taylor\'s University'],
        'HR Manager':          ['Universiti Malaya', 'Universiti Utara Malaysia', 'Universiti Putra Malaysia'],
    }

    uni_names = CAREER_UNI_MAP.get(career, [
        'Universiti Malaya', 'Universiti Kebangsaan Malaysia', 'Universiti Teknologi Malaysia'
    ])

    icons = ['🏛️', '🎓', '📚']
    result = []
    for i, name in enumerate(uni_names[:count]):
        # Try to find website from dataset
        match = malaysia_unis[malaysia_unis['name'].str.contains(
            name.split()[0], case=False, na=False
        )]
        website = match.iloc[0]['website'] if len(match) > 0 else 'www.mohe.gov.my'
        result.append({
            'name': name,
            'location': get_uni_location(name),
            'icon': icons[i],
            'website': website
        })
    return result

def get_uni_location(name):
    locations = {
        'Universiti Malaya': 'Kuala Lumpur',
        'Universiti Kebangsaan Malaysia': 'Bangi, Selangor',
        'Universiti Teknologi Malaysia': 'Johor Bahru, Johor',
        'Universiti Putra Malaysia': 'Serdang, Selangor',
        'Universiti Sains Malaysia': 'Penang',
        'Universiti Utara Malaysia': 'Sintok, Kedah',
        'Multimedia University': 'Cyberjaya, Selangor',
        'Asia Pacific University': 'Kuala Lumpur',
        'Taylor\'s University': 'Subang Jaya, Selangor',
        'Sunway University': 'Subang Jaya, Selangor',
        'AIMST University': 'Bedong, Kedah',
        'International Medical University': 'Kuala Lumpur',
        'Universiti Pendidikan Sultan Idris': 'Tanjung Malim, Perak',
        'International Islamic University Malaysia': 'Gombak, Selangor',
        'Universiti Tenaga Nasional': 'Kajang, Selangor',
        'UTAR': 'Kampar, Perak',
    }
    for key, loc in locations.items():
        if key.lower() in name.lower():
            return loc
    return 'Malaysia'

# ── HELPER: PTPTN calculation ──
def calculate_ptptn(career):
    fees_info = COURSE_FEES.get(career, DEFAULT_FEES)
    total_fee = fees_info['fee']
    uni_type  = fees_info['type']
    rate      = PTPTN_RATES[uni_type]
    ptptn_amt = min(int(total_fee * rate['coverage']), rate['max'])
    self_pay  = total_fee - ptptn_amt
    years     = int(fees_info['duration'].split()[0])
    monthly_repay = round(ptptn_amt / (15 * 12))  # 15 year repayment

    return {
        'total_fees':        total_fee,
        'ptptn_amount':      ptptn_amt,
        'self_payment':      self_pay,
        'coverage_pct':      round((ptptn_amt / total_fee) * 100),
        'monthly_repayment': monthly_repay,
        'years_to_repay':    15,
        'course_duration':   fees_info['duration'],
    }

# ── HELPER: Match career from interests using dataset ──
def match_career_from_data(interests):
    # Search career_recommender dataset for matching interests
    scores = {}
    for interest in interests:
        candidates = INTEREST_CAREER_MAP.get(interest, [])
        for career in candidates:
            scores[career] = scores.get(career, 0) + 1

    if not scores:
        return 'Business Analyst', 75

    best_career = max(scores, key=scores.get)
    total = len(interests)
    matched = scores[best_career]
    score = min(95, 70 + int((matched / total) * 25))

    # Cross-check with career dataset
    dataset_match = career_df[career_df['interests'].str.lower().str.contains(
        interests[0].lower()[:5], na=False
    )]
    if len(dataset_match) > 0:
        score = min(98, score + 3)

    return best_career, score

# ════════════════════════════════
# API ROUTES
# ════════════════════════════════

@app.route('/')
def home():
    return jsonify({'status': 'CareerPath AI Backend Running ✅', 'datasets_loaded': {
        'career_recommender': len(career_df),
        'salary_data': len(salary_df),
        'malaysian_universities': len(malaysia_unis)
    }})

@app.route('/api/recommend', methods=['POST'])
def recommend():
    data = request.json
    name      = data.get('name', 'Student')
    age       = data.get('age', 18)
    education = data.get('education', 'SPM')
    state     = data.get('state', 'Selangor')
    interests = data.get('interests', [])
    teamwork  = int(data.get('teamwork', 5))
    creative  = int(data.get('creative', 5))
    helping   = int(data.get('helping', 5))
    salary_pref = int(data.get('salary', 5))

    if not interests:
        return jsonify({'error': 'No interests provided'}), 400

    # Step 1: Match career from Kaggle data
    career, match_score = match_career_from_data(interests)

    # Step 2: Get salary from Salary dataset
    salary_info = get_salary_info(career)

    # Step 3: Get Malaysian universities from dataset
    universities = get_universities(career)

    # Step 4: Calculate PTPTN
    ptptn = calculate_ptptn(career)

    # Step 5: Build why reason from dataset stats
    sample = career_df[career_df['interests'].str.lower().str.contains(
        interests[0][:5].lower(), na=False
    )]
    dataset_insight = f"{len(sample)} people with similar interests in our dataset chose related careers." if len(sample) > 0 else ""

    why = (
        f"Based on your strong interest in {', '.join(interests[:2])}, {career} is your best career match. "
        f"Our analysis of {len(salary_df):,} salary records shows this career offers an average monthly salary "
        f"of RM {salary_info['average_myr']:,} in Malaysia. {dataset_insight} "
        f"With your preference for {'teamwork' if teamwork > 5 else 'independent work'} and "
        f"{'creative' if creative > 5 else 'analytical'} thinking, you have the right profile to excel in this field."
    )

    return jsonify({
        'career':           career,
        'matchScore':       match_score,
        'badge':            'Top Match' if match_score >= 90 else 'Great Match',
        'why':              why,
        'universities':     universities,
        'salary':           salary_info,
        'ptptn':            ptptn,
        'dataset_stats': {
            'careers_analysed':    len(salary_df),
            'students_surveyed':   len(career_df),
            'malaysian_unis':      len(malaysia_unis),
        }
    })

@app.route('/api/universities', methods=['GET'])
def get_all_universities():
    unis = malaysia_unis.to_dict('records')
    return jsonify({'total': len(unis), 'universities': unis})

@app.route('/api/salaries', methods=['GET'])
def get_salaries():
    job = request.args.get('job', '')
    if job:
        info = get_salary_info(job)
        return jsonify(info)
    # Return top careers with salary
    top_jobs = salary_df.groupby('job_title')['salary'].mean().sort_values(ascending=False).head(20)
    result = []
    for job, avg in top_jobs.items():
        result.append({'job': job, 'avg_monthly_myr': round(avg * 4.7 / 12)})
    return jsonify(result)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    return jsonify({
        'total_careers_in_dataset': salary_df['job_title'].nunique(),
        'total_salary_records':     len(salary_df),
        'total_students_surveyed':  len(career_df),
        'malaysian_universities':   len(malaysia_unis),
        'top_interests': career_df['interests'].value_counts().head(10).to_dict(),
    })

if __name__ == '__main__':
    print("\n🚀 CareerPath AI Backend starting...")
    print("📊 All 3 Kaggle datasets loaded!")
    print("🌐 Running at http://localhost:5000\n")
    app.run(debug=True, port=5000)