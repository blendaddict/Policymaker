import React, { useState } from 'react';
import { FormControl, InputLabel, Select, MenuItem } from '@mui/material';

function SortingDropdown({ callback }) {
    const allOptions = [
        "Age", "Census Division", "Education", "Sexuality", "Gender", "Income", "Neighborhood", "Political Ideology", 
        "Political Party Preference", "Marital Status", "Employment Status"
      ]
    const [selectedOption, setSelectedOption] = useState(allOptions[0]);

    const handleChange = (event) => {
        setSelectedOption(event.target.value);
        callback(event.target.value)
    };

    return (
        <FormControl sx={{ width: '48%' }}>
        <InputLabel id="dropdown-label">Sort Blobs</InputLabel>
        <Select
            labelId="dropdown-label"
            value={selectedOption}
            label="Select a sorting criterion"
            onChange={handleChange}
        >
            {
                allOptions.map((option) => (
                    <MenuItem key={option} value={option}>
                        {option}
                    </MenuItem>
                ))
            }
        </Select>
        </FormControl>
    );
}

export { SortingDropdown }