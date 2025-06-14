import streamlit as st
import numpy as np
import pandas as pd

# --- Constants ---
MAX_SCORE = 1000
NUM_DUMMY_UNIVERSITIES = 1000  # Number of hypothetical universities for percentile calculation

# --- Normalization Functions ---
def min_max_scale(value, min_val, max_val):
    """Scales a value to a 0-10 range using Min-Max scaling."""
    if max_val == min_val:
        return 0.0  # Avoid division by zero if all values are the same
    return 10 * (value - min_val) / (max_val - min_val)

def percentile_score(value, data_series):
    """Calculates the percentile rank of a value within a given data series and scales to 0-10."""
    data_series = np.array(data_series)
    if len(data_series) == 0:
        return 0.0
    
    # Count values less than 'value' and values equal to 'value'
    less_than_count = np.sum(data_series < value)
    equal_to_count = np.sum(data_series == value)
    
    # Percentile rank formula: (count_less_than + 0.5 * count_equal_to) / total_count
    percentile_rank = (less_than_count + 0.5 * equal_to_count) / len(data_series)
    return 10 * percentile_rank  # Scale to 0-10

def survey_adjust(avg_rating):
    """Transforms an average Likert scale rating (1-5) to a 0-10 score."""
    # Score = 2.5 * (Avg. Rating - 1)
    return 2.5 * (avg_rating - 1)

# --- Dummy Data Generation for Percentile Calculation ---
# These ranges are illustrative and can be adjusted to reflect realistic distributions
dummy_data_ranges = {
    "Expertise_h_index": (1, 50),  # h-index range
    "Approachability_feedback_scores": (0, 10),  # feedback scores (already 0-10 after initial survey_adjust)
    "Placement_Rate": (0.5, 0.99),  # percentage (50% to 99%)
    "Alumni_Salary": (50000, 200000),  # illustrative salary range
    "Research_Output_FWCI": (0.1, 5.0),  # FWCI/CNCI range
    "Research_Funding_per_student": (1000, 50000),  # dollars per student range
    "PhD_Conferred": (10, 500),  # number of PhDs conferred annually
    "Funding_Opportunities": (0, 10000)  # average grants per student
}

# Generate random dummy data for the specified number of universities
dummy_data = {}
for metric, (min_val, max_val) in dummy_data_ranges.items():
    dummy_data[metric] = np.random.uniform(min_val, max_val, NUM_DUMMY_UNIVERSITIES)

# --- Factor Calculation Functions ---
# Each function calculates the score for a main factor based on its sub-metrics and local weights.
# It also returns the normalized sub-metric scores for transparency.

def calculate_qtf(expertise_h_index, clarity_avg_rating, approachability_feedback_score):
    """Calculates Quality of Teaching Faculty (QTF) score."""
    # Sub-metric Normalization (to 0-10)
    expertise_score = min_max_scale(expertise_h_index, *dummy_data_ranges["Expertise_h_index"])
    clarity_score = survey_adjust(clarity_avg_rating)  # Input 1-5, output 0-10
    approachability_score = percentile_score(approachability_feedback_score, dummy_data["Approachability_feedback_scores"])

    # Local Weights: Expertise (40%), Clarity (30%), Approachability (30%)
    qtf_score = (0.40 * expertise_score +
                 0.30 * clarity_score +
                 0.30 * approachability_score)
    return qtf_score, {
        "Expertise Score": expertise_score,
        "Clarity Score": clarity_score,
        "Approachability Score": approachability_score
    }

def calculate_tm(lecture_effectiveness, discussion_based_pct, practical_sessions_hours):
    """Calculates Teaching Methods (TM) score."""
    # Sub-metric Normalization (assuming inputs are already on a 0-10 scale after internal transformations)
    lecture_score = lecture_effectiveness
    discussion_score = discussion_based_pct
    practical_score = practical_sessions_hours

    # Local Weights: Lectures (30%), Discussions (40%), Practical (30%)
    tm_score = (0.30 * lecture_score +
                0.40 * discussion_score +
                0.30 * practical_score)
    return tm_score, {
        "Lecture Effectiveness Score": lecture_score,
        "Discussion-based Score": discussion_score,
        "Practical Sessions Score": practical_score
    }

def calculate_ps(placement_rate, employer_reputation, industry_partnerships, alumni_salary, entrepreneurial_success):
    """Calculates University's Placement Services (PS) score."""
    # Sub-metric Normalization (to 0-10)
    placement_score = percentile_score(placement_rate, dummy_data["Placement_Rate"])
    employer_score = survey_adjust(employer_reputation)  # Input 1-5, output 0-10
    industry_score = min_max_scale(industry_partnerships, 0, 100)  # Assuming max 100 partnerships for scaling
    alumni_salary_score = percentile_score(alumni_salary, dummy_data["Alumni_Salary"])
    entrepreneurial_score = min_max_scale(entrepreneurial_success, 0, 20)  # Assuming max 20 startups for scaling

    # Local Weights (adjusted for 5 sub-metrics as per report):
    # Graduate Employment Rate (0.30), Employer Reputation (0.20), Industry Partnerships (0.20),
    # Alumni Career Progression (0.15), Start-up & Entrepreneurial Success (0.15)
    ps_score = (0.30 * placement_score +
                0.20 * employer_score +
                0.20 * industry_score +
                0.15 * alumni_salary_score +
                0.15 * entrepreneurial_score)
    return ps_score, {
        "Placement Rate Score": placement_score,
        "Employer Reputation Score": employer_score,
        "Industry Partnerships Score": industry_score,
        "Alumni Salary Progression Score": alumni_salary_score,
        "Entrepreneurial Success Score": entrepreneurial_score
    }

def calculate_cc(inclusion_index, representation_quotient, student_engagement_rate, retention_ratio_diverse_groups, cultural_competency_completion):
    """Calculates Campus Culture (CC) score."""
    # Sub-metric Normalization (assuming inputs are already on a 0-10 scale for percentages)
    inclusion_score = survey_adjust(inclusion_index)  # Input 1-5, output 0-10
    representation_score = representation_quotient
    engagement_score = student_engagement_rate
    retention_score = retention_ratio_diverse_groups
    cultural_score = cultural_competency_completion

    # Local Weights (adjusted for 5 sub-metrics as per report):
    # Inclusion Index (0.30), Representation Quotient (0.20), Student Engagement (0.20),
    # Retention Ratio (0.15), Cultural Competency (0.15)
    cc_score = (0.30 * inclusion_score +
                0.20 * representation_score +
                0.20 * engagement_score +
                0.15 * retention_score +
                0.15 * cultural_score)
    return cc_score, {
        "Inclusion Index Score": inclusion_score,
        "Representation Quotient Score": representation_score,
        "Student Engagement Rate Score": engagement_score,
        "Retention Ratio of Diverse Groups Score": retention_score,
        "Cultural Competency Training Completion Score": cultural_score
    }

def calculate_ro(research_expenditure, phd_attainment, research_output_fwci, lab_accessibility, funding_opportunities, mentorship_programs):
    """Calculates Research Opportunities (RO) score."""
    # Sub-metric Normalization (to 0-10)
    research_exp_score = min_max_scale(research_expenditure, *dummy_data_ranges["Research_Funding_per_student"])
    phd_score = min_max_scale(phd_attainment, *dummy_data_ranges["PhD_Conferred"])
    research_output_score = percentile_score(research_output_fwci, dummy_data["Research_Output_FWCI"])
    lab_score = survey_adjust(lab_accessibility)  # Input 1-5, output 0-10
    funding_score = min_max_scale(funding_opportunities, *dummy_data_ranges["Funding_Opportunities"])
    mentorship_score = survey_adjust(mentorship_programs)  # Input 1-5, output 0-10

    # Local Weights (adjusted for 6 sub-metrics as per report):
    # Research Expenditure (0.20), PhD Attainment (0.15), Research Output (0.25),
    # Lab Accessibility (0.15), Funding Opportunities (0.15), Mentorship Programs (0.10)
    ro_score = (0.20 * research_exp_score +
                0.15 * phd_score +
                0.25 * research_output_score +
                0.15 * lab_score +
                0.15 * funding_score +
                0.10 * mentorship_score)
    return ro_score, {
        "Research Expenditure Score": research_exp_score,
        "PhD Attainment Score": phd_score,
        "Research Output (FWCI/CNCI) Score": research_output_score,
        "Lab/Resource Accessibility Score": lab_score,
        "Funding Opportunities Score": funding_score,
        "Mentorship Programs Score": mentorship_score
    }

# --- Streamlit App Layout ---
st.set_page_config(layout="wide", page_title="Adaptive Holistic University Ranking System")

st.title("Adaptive Holistic University Ranking System")
st.markdown("A novel, dynamic algorithm for ranking universities based on 5 key factors.")

st.header("1. Input University Data (Scores out of 10, unless specified)")

# Global Weights Selection in Sidebar
st.sidebar.header("Global Weighting Scheme")
weight_scheme = st.sidebar.selectbox(
    "Select Global Weighting Scheme:",
    ("Default", "Research-focused", "Teaching-focused", "Custom")
)

# Predefined Global Weights
global_weights_presets = {
    "Default": {"QTF": 0.25, "TM": 0.20, "PS": 0.20, "CC": 0.15, "RO": 0.20},
    "Research-focused": {"QTF": 0.20, "TM": 0.15, "PS": 0.15, "CC": 0.10, "RO": 0.30},
    "Teaching-focused": {"QTF": 0.35, "TM": 0.30, "PS": 0.15, "CC": 0.10, "RO": 0.10}
}

current_weights = {}
if weight_scheme == "Custom":
    st.sidebar.subheader("Custom Global Weights (Sum to 100%)")
    custom_qtf = st.sidebar.slider("Quality of Teaching Faculty (QTF)", 0, 100, 25)
    custom_tm = st.sidebar.slider("Teaching Methods (TM)", 0, 100, 20)
    custom_ps = st.sidebar.slider("Placement Services (PS)", 0, 100, 20)
    custom_cc = st.sidebar.slider("Campus Culture (CC)", 0, 100, 15)
    custom_ro = st.sidebar.slider("Research Opportunities (RO)", 0, 100, 20)
    
    total_custom_weight = custom_qtf + custom_tm + custom_ps + custom_cc + custom_ro
    if total_custom_weight != 100:
        st.sidebar.warning(f"Custom weights sum to {total_custom_weight}%. Adjusting to 100% for calculation.")
        # Normalize if not 100 to allow calculation, but warn user
        norm_factor = 100 / total_custom_weight if total_custom_weight > 0 else 0
        current_weights = {
            "QTF": custom_qtf * norm_factor / 100,
            "TM": custom_tm * norm_factor / 100,
            "PS": custom_ps * norm_factor / 100,
            "CC": custom_cc * norm_factor / 100,
            "RO": custom_ro * norm_factor / 100
        }
    else:
        current_weights = {
            "QTF": custom_qtf / 100,
            "TM": custom_tm / 100,
            "PS": custom_ps / 100,
            "CC": custom_cc / 100,
            "RO": custom_ro / 100
        }
else:
    current_weights = global_weights_presets[weight_scheme]

st.sidebar.markdown("---")
st.sidebar.subheader("Current Global Weights:")
for factor, weight in current_weights.items():
    st.sidebar.write(f"{factor}: {weight*100:.1f}%")

# Input sections for each factor in main columns
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Factor 1: Quality of Teaching Faculty (QTF)")
    qtf_expertise_h_index = st.number_input("Expertise (h-index, e.g., 1-50)", min_value=1.0, max_value=50.0, value=25.0, step=1.0, key="qtf_exp")
    qtf_clarity_avg_rating = st.number_input("Clarity (Avg. Student Rating 1-5)", min_value=1.0, max_value=5.0, value=4.0, step=0.1, key="qtf_clarity")
    qtf_approachability_feedback_score = st.number_input("Approachability (Student Feedback Score 0-10)", min_value=0.0, max_value=10.0, value=7.0, step=0.1, key="qtf_app")

with col2:
    st.subheader("Factor 2: Teaching Methods (TM)")
    tm_lecture_effectiveness = st.number_input("Lecture Effectiveness (0-10)", min_value=0.0, max_value=10.0, value=7.5, step=0.1, key="tm_lec")
    tm_discussion_based_pct = st.number_input("Discussion-based (% courses with seminars 0-10)", min_value=0.0, max_value=10.0, value=6.0, step=0.1, key="tm_disc")
    tm_practical_sessions_hours = st.number_input("Practical Sessions (Lab/fieldwork hours per course 0-10)", min_value=0.0, max_value=10.0, value=8.0, step=0.1, key="tm_prac")

with col3:
    st.subheader("Factor 3: University's Placement Services (PS)")
    ps_placement_rate = st.number_input("Graduate Employment Rate (e.g., 0.5-0.99)", min_value=0.0, max_value=1.0, value=0.85, step=0.01, key="ps_place")
    ps_employer_reputation = st.number_input("Employer Reputation (Avg. Rating 1-5)", min_value=1.0, max_value=5.0, value=3.8, step=0.1, key="ps_emp")
    ps_industry_partnerships = st.number_input("Industry Partnerships (Number, e.g., 0-100)", min_value=0, max_value=100, value=50, step=1, key="ps_ind")
    ps_alumni_salary = st.number_input("Alumni Career Progression (Avg. Salary, e.g., 50000-200000)", min_value=0.0, max_value=300000.0, value=75000.0, step=1000.0, key="ps_alumni")
    ps_entrepreneurial_success = st.number_input("Entrepreneurial Success (Number of student-founded ventures, e.g., 0-20)", min_value=0, max_value=50, value=5, step=1, key="ps_ent")

col4, col5 = st.columns(2)

with col4:
    st.subheader("Factor 4: Campus Culture (CC)")
    cc_inclusion_index = st.number_input("Inclusion Index (Avg. Student Rating 1-5)", min_value=1.0, max_value=5.0, value=4.2, step=0.1, key="cc_inc")
    cc_representation_quotient = st.number_input("Representation Quotient (% diverse students/faculty 0-10)", min_value=0.0, max_value=10.0, value=7.0, step=0.1, key="cc_rep")
    cc_student_engagement_rate = st.number_input("Student Engagement Rate (% active in clubs/activities 0-10)", min_value=0.0, max_value=10.0, value=8.0, step=0.1, key="cc_eng")
    cc_retention_ratio_diverse_groups = st.number_input("Retention Ratio of Diverse Groups (% retained 0-10)", min_value=0.0, max_value=10.0, value=7.5, step=0.1, key="cc_ret")
    cc_cultural_competency_completion = st.number_input("Cultural Competency Training Completion (% students 0-10)", min_value=0.0, max_value=10.0, value=6.5, step=0.1, key="cc_cult")

with col5:
    st.subheader("Factor 5: Research Opportunities (RO)")
    ro_research_expenditure = st.number_input("Research Expenditure (per student, e.g., 1000-50000)", min_value=0.0, max_value=100000.0, value=25000.0, step=100.0, key="ro_exp")
    ro_phd_attainment = st.number_input("PhD Attainment (Number of PhDs conferred annually, e.g., 10-500)", min_value=0, max_value=1000, value=200, step=1, key="ro_phd")
    ro_research_output_fwci = st.number_input("Research Output (FWCI/CNCI, e.g., 0.1-5.0)", min_value=0.0, max_value=10.0, value=2.5, step=0.1, key="ro_fwci")
    ro_lab_accessibility = st.number_input("Lab/Resource Accessibility (Avg. Student Rating 1-5)", min_value=1.0, max_value=5.0, value=4.5, step=0.1, key="ro_lab")
    ro_funding_opportunities = st.number_input("Funding Opportunities (Avg. internal/external grants per student, e.g., 0-10000)", min_value=0.0, max_value=20000.0, value=5000.0, step=100.0, key="ro_fund")
    ro_mentorship_programs = st.number_input("Mentorship Programs (Avg. Student Rating 1-5)", min_value=1.0, max_value=5.0, value=4.0, step=0.1, key="ro_ment")

st.markdown("---")

if st.button("Calculate University Score"):
    # Calculate raw factor scores (0-10)
    qtf_score_raw, qtf_sub_scores = calculate_qtf(qtf_expertise_h_index, qtf_clarity_avg_rating, qtf_approachability_feedback_score)
    tm_score_raw, tm_sub_scores = calculate_tm(tm_lecture_effectiveness, tm_discussion_based_pct, tm_practical_sessions_hours)
    ps_score_raw, ps_sub_scores = calculate_ps(ps_placement_rate, ps_employer_reputation, ps_industry_partnerships, ps_alumni_salary, ps_entrepreneurial_success)
    cc_score_raw, cc_sub_scores = calculate_cc(cc_inclusion_index, cc_representation_quotient, cc_student_engagement_rate, cc_retention_ratio_diverse_groups, cc_cultural_competency_completion)
    ro_score_raw, ro_sub_scores = calculate_ro(ro_research_expenditure, ro_phd_attainment, ro_research_output_fwci, ro_lab_accessibility, ro_funding_opportunities, ro_mentorship_programs)

    raw_factor_scores = {
        "QTF": qtf_score_raw,
        "TM": tm_score_raw,
        "PS": ps_score_raw,
        "CC": cc_score_raw,
        "RO": ro_score_raw
    }

    # Generate dummy data for overall factor scores for percentile calculation
    # This simulates a distribution of scores for other universities for each factor
    dummy_overall_factor_scores = {
        "QTF": np.random.uniform(0, 10, NUM_DUMMY_UNIVERSITIES),
        "TM": np.random.uniform(0, 10, NUM_DUMMY_UNIVERSITIES),
        "PS": np.random.uniform(0, 10, NUM_DUMMY_UNIVERSITIES),
        "CC": np.random.uniform(0, 10, NUM_DUMMY_UNIVERSITIES),
        "RO": np.random.uniform(0, 10, NUM_DUMMY_UNIVERSITIES),
    }

    adjusted_factor_scores = {}
    for factor, score_raw in raw_factor_scores.items():
        # Add the current university's score to the dummy data for percentile calculation
        temp_data_for_percentile = np.append(dummy_overall_factor_scores[factor], score_raw)
        
        # Calculate percentile rank for the raw factor score (0-1 scale)
        percentile_rank_factor = percentile_score(score_raw, temp_data_for_percentile) / 10 
        
        # Peer-Adjusted Scoring: F_i' = 0.7 * F_i + 0.3 * Percentile(F_i)
        # Note: Percentile(F_i) in the formula is on a 0-10 scale, so we multiply percentile_rank_factor by 10
        adjusted_factor_scores[factor] = (0.7 * score_raw) + (0.3 * percentile_rank_factor * 10) 

    # Non-Linear Aggregation
    # Base Score: Base = sum(w_i * F_i')
    base_score = sum(current_weights[f] * adjusted_factor_scores[f] for f in raw_factor_scores)

    # Synergy Bonus: If >=3 factors score >7
    high_scoring_factors = [score for score in adjusted_factor_scores.values() if score > 7]
    synergy_bonus = 0
    if len(high_scoring_factors) >= 3:
        # Take the average of the top 3 high-scoring factors
        avg_top_3 = np.mean(sorted(high_scoring_factors, reverse=True)[:3])
        synergy_bonus = 0.5 * (avg_top_3 - 7)
        if synergy_bonus < 0: synergy_bonus = 0  # Ensure bonus is not negative

    # Penalty: For any factor <3
    failing_factors_count = sum(1 for score in adjusted_factor_scores.values() if score < 3)
    penalty = 0.2 * failing_factors_count

    # Final Score (0-10 scale)
    final_score_0_10 = base_score + synergy_bonus - penalty
    
    # Ensure final score is within 0-10 range
    final_score_0_10 = max(0, min(10, final_score_0_10))

    # Scale to 1000 max
    final_score_1000 = (final_score_0_10 / 10) * MAX_SCORE
    
    st.markdown(f"## Final University Score: **{final_score_1000:.2f} / {MAX_SCORE}**")
    
    with st.expander("Calculation Results"):    

        st.subheader("Sub-Metric Scores (0-10 Scale)")
        st.json({
            "Quality of Teaching Faculty": {k: f"{v:.2f}" for k, v in qtf_sub_scores.items()},
            "Teaching Methods": {k: f"{v:.2f}" for k, v in tm_sub_scores.items()},
            "Placement Services": {k: f"{v:.2f}" for k, v in ps_sub_scores.items()},
            "Campus Culture": {k: f"{v:.2f}" for k, v in cc_sub_scores.items()},
            "Research Opportunities": {k: f"{v:.2f}" for k, v in ro_sub_scores.items()}
        })

        st.subheader("Raw Factor Scores (0-10 Scale)")
        st.json({f: f"{s:.2f}" for f, s in raw_factor_scores.items()})

        st.subheader("Peer-Adjusted Factor Scores (0-10 Scale)")
        st.json({f: f"{s:.2f}" for f, s in adjusted_factor_scores.items()})

        st.subheader("Non-Linear Aggregation Details")
        st.write(f"Base Score: {base_score:.2f}")
        st.write(f"Synergy Bonus: {synergy_bonus:.2f}")
        st.write(f"Penalty: {penalty:.2f}")


# Documentation
st.header("Algorithm Documentation")
with st.expander("Detailed Algorithm Explanation"):
    st.markdown("""
    ## Multi-Criteria Decision Analysis Framework for University Ranking
    
    This algorithm evaluates universities across five critical dimensions using advanced Multi-Criteria Decision Analysis (MCDA) techniques with non-linear aggregation and adaptive weighting.
    
    ### Key Components:
    
    1. **Factor Evaluation**:
       - Quality of Teaching Faculty (QTF)
       - Teaching Methods (TM)
       - Placement Services (PS)
       - Campus Culture (CC)
       - Research Opportunities (RO)
    
    2. **Non-Linear Aggregation**:
       - Base Score: Weighted sum of adjusted factor scores
       - Synergy Bonus: Reward for holistic excellence (≥3 factors >7)
       - Penalty: For significant underperformance (any factor <3)
    
    3. **Peer-Adjusted Scoring**:
       - Combines raw scores with percentile ranks (70/30 blend)
       - Reduces impact of outliers and provides relative performance context
    
    ### Mathematical Formulation:
    
    **Base Score**:
    \[
    \text{Base} = \sum_{i=1}^{5} w_i \times F_i'
    \]
    Where \(w_i\) is the weight and \(F_i'\) is the peer-adjusted score for factor \(i\).
    
    **Synergy Bonus**:
    \[
    \text{Bonus} = 
    \begin{cases} 
    0.5 \times (\text{AvgTop3} - 7) & \text{if } \geq 3 \text{ factors } > 7 \\
    0 & \text{otherwise}
    \end{cases}
    \]
    
    **Penalty**:
    \[
    \text{Penalty} = 0.2 \times \text{Number of factors } < 3
    \]
    
    **Final Score**:
    \[
    \text{Final} = 100 \times (\text{Base} + \text{Bonus} - \text{Penalty})
    \]
    (Scaled to 1000-point scale)
    """)

with st.expander("Factor Impact Analysis"):
    st.markdown("""
    ## Factor Impact on Final Score
    
    Each factor contributes to the final score based on its weight and performance relative to peers:
    
    ### 1. Quality of Teaching Faculty (QTF) - Default Weight: 25%
    - **Sub-metrics**: Expertise (40%), Clarity (30%), Approachability (30%)
    - **Impact**: Directly affects 25% of base score. Strong performance here can trigger synergy bonus.
    - **Rationale**: Teaching quality is fundamental to university mission. Research shows student outcomes strongly correlate with faculty quality.
    
    ### 2. Teaching Methods (TM) - Default Weight: 20%
    - **Sub-metrics**: Lectures (30%), Discussions (40%), Practical (30%)
    - **Impact**: Contributes 20% to base score. Active learning methods boost retention and outcomes.
    - **Rationale**: Pedagogy matters as much as content. Varied methods accommodate diverse learning styles.
    
    ### 3. Placement Services (PS) - Default Weight: 20%
    - **Sub-metrics**: Employment rate (50%), Employer satisfaction (30%), Alumni (20%)
    - **Impact**: 20% of base score. Critical for professional program rankings.
    - **Rationale**: Career outcomes are key measure of institutional effectiveness for many stakeholders.
    
    ### 4. Campus Culture (CC) - Default Weight: 15%
    - **Sub-metrics**: Inclusivity (40%), Engagement (30%), Balance (30%)
    - **Impact**: 15% of base score, but affects student satisfaction and retention.
    - **Rationale**: Positive campus environment enhances learning and personal development.
    
    ### 5. Research Opportunities (RO) - Default Weight: 20%
    - **Sub-metrics**: Expenditure (20%), PhD output (10%), Research impact (30%), Resources (40%)
    - **Impact**: 20% of base score. Strong research can compensate for weaker areas.
    - **Rationale**: Research drives innovation and attracts top talent, benefiting all students.
    
    ### Synergy Bonus
    - **Impact**: Up to +1.5 points (15 on 1000-scale) for universities strong in multiple areas
    - **Rationale**: Rewards comprehensive excellence over single-area strength
    
    ### Penalty
    - **Impact**: -0.2 points (-2 on 1000-scale) per failing factor (<3/10)
    - **Rationale**: Prevents masking of severe deficiencies in critical areas
    """)

with st.expander("Algorithm Comparison"):
    st.markdown("""
    ## Comparison with Traditional Ranking Methods
    
    | Feature                     | Traditional Rankings | This Algorithm |
    |----------------------------|----------------------|----------------|
    | **Weighting**              | Static, fixed        | Dynamic, adaptive |
    | **Aggregation**            | Linear (weighted sum)| Non-linear with bonuses/penalties |
    | **Peer Comparison**        | Absolute metrics     | Relative percentile adjustment |
    | **Teaching Evaluation**    | Often research proxies| Direct measures of pedagogy |
    | **Holistic Assessment**    | Limited              | Synergy bonus for comprehensive excellence |
    | **Deficiency Handling**    | Compensatory         | Penalties for critical weaknesses |
    | **Customization**          | One-size-fits-all    | Adjustable weights by stakeholder |
    | **Transparency**           | Often opaque         | Fully documented methodology |
    
    **Key Advantages**:
    1. More nuanced evaluation that prevents strong performance in one area from masking weaknesses in others
    2. Dynamic weighting accommodates different stakeholder priorities
    3. Peer-adjusted scoring provides fair comparison across institutional contexts
    4. Non-linear aggregation better reflects real-world quality thresholds
    """)

with st.expander("Implementation Notes"):
    st.markdown("""
    ## Implementation Considerations
    
    ### Data Requirements
    - Quantitative metrics (employment rates, research expenditure)
    - Qualitative surveys (student evaluations, employer feedback)
    - Institutional data (course syllabi, faculty profiles)
    
    ### Computational Complexity
    - Peer-adjusted scoring requires pairwise comparisons
    - Synergy bonus calculation scales with number of factors
    - Weight optimization can be computationally intensive
    
    ### Ethical Considerations
    - Transparent methodology to prevent gaming
    - Careful handling of sensitive data (student surveys)
    - Regular audits to ensure fairness
    
    ### Limitations
    - Reliance on self-reported data for some metrics
    - Challenges normalizing across disciplines/institutions
    - Requires comprehensive data collection infrastructure
    """)