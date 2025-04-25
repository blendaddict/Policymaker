import random

def generate_random_data_with_weights(num_samples=100):
    data = []

    ages = ['18 to 24', '25 to 34', '35 to 44', '45 to 54', '55 to 64', '65 to 74', '75 or more']
    age_weights = [11.03, 13.88, 17.49, 19.77, 21.48, 13.50, 2.85]

    census_divisions = ['New England', 'Middle Atlantic', 'E.N. Central', 'W.N. Central', 'South Atlantic', 'E.S. Central', 'W.S. Central', 'Mountain', 'Pacific', 'Foreign']
    census_weights = [6.65, 12.83, 18.73, 8.08, 10.08, 11.5, 8.65, 5.13, 15.78, 2.57]

    education_levels = ['Less than high school graduate', 'High school graduate', 'Associate/junior college', "Bachelor's degree", 'Graduate degree']
    education_weights = [2.28, 38.88, 17.59, 26.9, 14.35]

    sexualities = ['Heterosexual/straight', 'Gay or lesbian', 'Bisexual', 'Asexual', 'Pansexual', 'Other sexual orientation']
    sexuality_weights = [82.2, 4.36, 8.04, 1.72, 2.41, 1.15]

    genders = ['Female', 'Male']
    gender_weights = [56.37, 43.63]

    incomes = ['Less than $25,000', '$25,000 to $34,999', '$35,000 to $49,999', '$50,000 to $74,999', '$75,000 to $99,999', '$100,000 to $124,999', '$125,000 to $149,999', '$150,000 to $174,999', '$175,000 to $199,999', '$200,000 to $249,999', '$250,000 or more']
    income_weights = [18.83, 11.83, 13.89, 20.44, 14.7, 8.04, 5.05, 2.18, 1.61, 1.38, 2.18]

    neighborhoods = ['Urban', 'Suburban', 'Rural']
    neighborhood_weights = [30.88, 48.11, 21.13]

    political_ideologies = ['Extremely Liberal', 'Liberal', 'Slightly Liberal', 'Moderate', 'Slightly conservative', 'Conservative', 'Extremely conservative']
    ideology_weights = [11.31, 19.01, 9.32, 28.8, 8.94, 16.83, 5.8]

    political_preferences = ['Strong Democrat', 'Democrat', 'Independent, close to Dem.', 'Independent', 'Independent, close to Rep.', 'Republican', 'Strong Republican', 'Other']
    preference_weights = [21.96, 13.31, 11.88, 15.59, 8.46, 11.6, 14.83, 2.38]

    marital_statuses = ['Single', 'Married', 'Separated', 'Divorced', 'Widowed']
    marital_weights = [30, 50, 5, 10, 5]  # Example probabilities, adjust as needed

    employment_statuses = ['Employed', 'Unemployed', 'Student', 'Retired', 'Self-employed']
    employment_weights = [50, 10, 15, 20, 5]  # Example probabilities, adjust as needed

    for _ in range(num_samples):
        sample = {
            'Age': random.choices(ages, weights=age_weights, k=1)[0],
            'Census Division': random.choices(census_divisions, weights=census_weights, k=1)[0],
            'Education': random.choices(education_levels, weights=education_weights, k=1)[0],
            'Sexuality': random.choices(sexualities, weights=sexuality_weights, k=1)[0],
            'Gender': random.choices(genders, weights=gender_weights, k=1)[0],
            'Income': random.choices(incomes, weights=income_weights, k=1)[0],
            'Neighborhood': random.choices(neighborhoods, weights=neighborhood_weights, k=1)[0],
            'Political Ideology': random.choices(political_ideologies, weights=ideology_weights, k=1)[0],
            'Political Party Preference': random.choices(political_preferences, weights=preference_weights, k=1)[0],
            'Marital Status': random.choices(marital_statuses, weights=marital_weights, k=1)[0],
            'Employment Status': random.choices(employment_statuses, weights=employment_weights, k=1)[0],
        }
        data.append(sample)

    return data

# Example usage:
#random_data = generate_random_data_with_weights(num_samples=5)
#for entry in random_data:
#    print(entry)