import { floorLevel } from "./components/Blob";

const properties = {
    "Age": ['18 to 24', '25 to 34', '35 to 44', '45 to 54', '55 to 64', '65 to 74', '75 or more'],
    "Census Division": ['New England', 'Middle Atlantic', 'E.N. Central', 'W.N. Central', 'South Atlantic', 'E.S. Central', 'W.S. Central', 'Mountain', 'Pacific', 'Foreign'],
    "Education": ['Less than high school graduate', 'High school graduate', 'Associate/junior college', "Bachelor's degree", 'Graduate degree'],
    "Sexuality": ['Heterosexual/straight', 'Gay or lesbian', 'Bisexual', 'Asexual', 'Pansexual', 'Other sexual orientation'],
    "Gender": ["Female", "Male"],
    "Income": ['Less than $25,000', '$25,000 to $34,999', '$35,000 to $49,999', '$50,000 to $74,999', '$75,000 to $99,999', '$100,000 to $124,999', '$125,000 to $149,999', '$150,000 to $174,999', '$175,000 to $199,999', '$200,000 to $249,999', '$250,000 or more'],
    "Neighborhood": ['Urban', 'Suburban', 'Rural'],
    "Political Ideology": ['Extremely Liberal', 'Liberal', 'Slightly Liberal', 'Moderate', 'Slightly conservative', 'Conservative', 'Extremely conservative'],
    "Political Party Preference": ['Strong Democrat', 'Democrat', 'Independent, close to Dem.', 'Independent', 'Independent, close to Rep.', 'Republican', 'Strong Republican', 'Other'],
    "Marital Status": ['Single', 'Married', 'Separated', 'Divorced', 'Widowed'],
    "Employment Status": ['Employed', 'Unemployed', 'Student', 'Retired', 'Self-employed']
}

function linspace(start, stop, num) {
    const result = [];
    if (num === 1) {
      result.push(start);
    } else {
      const step = (stop - start) / (num - 1);
      for (let i = 0; i < num; i++) {
        let x = start + step * i
        result.push([x, floorLevel, x]);
      }
    }
    return result;
  }

export function sortBlobs(blobs, blobRefs, category) {
    const possibleValues = properties[category]
    let indices = blobs.map((b, index) => [index, possibleValues.indexOf(b["properties"][category])])
    indices.sort((x, y) => x[1] - y[1])

    let positions = linspace(-1.5, 1.5, blobs.length)

    let blobIndices = indices.map(x => x[0])
    
    for (let i = 0; i < blobs.length; i++) {
        blobRefs.current[i].moveToPosition(positions[blobIndices[i]])
    }
}