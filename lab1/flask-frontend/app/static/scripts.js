const dropdownSelected = document.getElementById('dropdown-selected');
const dropdownOptions = document.getElementById('dropdown-options');
const submitButton = document.getElementById('submit-button');
const inputDataSection = document.getElementById('input-data-section');
const loadingIndicator = document.getElementById('loading');
const responseSection = document.getElementById('response-section');
const responseTable = document.getElementById('response-table').querySelector('tbody');
let selectedScenario = null;

// Toggle dropdown visibility
dropdownSelected.addEventListener('click', () => {
    dropdownOptions.style.display = dropdownOptions.style.display === 'block' ? 'none' : 'block';
});

// Handle option selection
dropdownOptions.addEventListener('click', (event) => {
    if (event.target && event.target.dataset.value) {
        selectedScenario = event.target.dataset.value;
        dropdownSelected.textContent = event.target.textContent;
        dropdownOptions.style.display = 'none';

        // Show the corresponding form fields
        document.querySelectorAll('.form-fields').forEach(field => {
            field.classList.remove('active');
        });
        const activeFields = document.getElementById(selectedScenario);
        if (activeFields) {
            activeFields.classList.add('active');
        }
    }
});

// Form submission
document.getElementById('scenario-form').addEventListener('submit', async (event) => {
    event.preventDefault();

    if (submitButton.textContent === 'Submit') {
        // Enter loading state
        inputDataSection.style.display = 'none';
        loadingIndicator.style.display = 'block';

        try {
            if (!selectedScenario) {
                throw new Error('Please select a scenario');
            }

            const activeFields = document.querySelector('.form-fields.active');
            const inputs = activeFields.querySelectorAll('input');
            const data = {};
            inputs.forEach(input => {
                key = input.id.split('_');
                if (selectedScenario === 'post_post' ||
                    selectedScenario === 'post_target' ||
                    selectedScenario === 'reg_user' ||
                    selectedScenario === 'reg_topic')
                    key = key.slice(2).join('_');
                else
                    key = key.slice(3).join('_');
                data[key] = input.value;
                if (input.value === '' && key !== 'parent') {
                    throw new Error('Please fill in all fields');
                }
                else if (key === 'score') {
                    data[key] = parseInt(data[key]);
                }
                else if (selectedScenario === 'post_post' && key === 'topic_id') {
                    data[key] = data[key].split(',').map(item => item.trim()).filter(item => item !== '');
                }
            });
            const textareas = activeFields.querySelectorAll('textarea');
            textareas.forEach(textarea => {
                key = textarea.id.split('_');
                key = key.slice(3).join('_');
                data[key] = textarea.value;
                if (textarea.value === '') {
                    throw new Error('Please fill in all fields');
                }
            });
            const response = await fetch('/api/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ scenario: selectedScenario, data }),
            });

            const res = await response.json();
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const result = JSON.parse(res);
            console.log(result);
            if (!result.status || result.status !== 200) {
                throw new Error(result.message || 'Unknown error occurred');
            }
            // Populate the table with the response
            responseTable.innerHTML = ''; // Clear previous results
            if (selectedScenario === 'reg_user' ||
                selectedScenario === 'reg_topic' ||
                selectedScenario === 'post_post' ||
                selectedScenario === 'post_target' ||
                selectedScenario === 'post_comment_score' ||
                selectedScenario === 'post_comment_comment') {
                loadingIndicator.textContent = 'Post successful';
                const keys = Object.keys(result.data);
                keys.forEach(key => {
                    const row = document.createElement('tr');
                    const th = document.createElement('th');
                    th.textContent = key;
                    row.appendChild(th);
                    const td = document.createElement('td');
                    td.textContent = result.data[key] || 'N/A';
                    row.appendChild(td);
                    responseTable.appendChild(row);
                });
                responseSection.style.display = 'block';
            }
            else {
                const data = result.data;
                console.log(data);
                if (selectedScenario === 'post_comment_score') {
                    if (!data || !data.score) {
                        throw new Error('Invalid data format');
                    }
                    const avg_score = data.score;
                    const headerRow = document.createElement('tr');
                    const th = document.createElement('th');
                    th.textContent = "average_score";
                    headerRow.appendChild(th);
                    const th2 = document.createElement('th');
                    th2.textContent = avg_score;
                    headerRow.appendChild(th2);
                    responseTable.appendChild(headerRow);
                }
                else {
                    if (!data || data.length === 0) {
                        throw new Error('Invalid data format');
                    }

                    const keys = Object.keys(data[0]);
                    const headerRow = document.createElement('tr');
                    keys.forEach(key => {
                        const th = document.createElement('th');
                        th.textContent = key;
                        headerRow.appendChild(th);
                    });
                    responseTable.appendChild(headerRow);
                    data.forEach(item => {
                        const row = document.createElement('tr');
                        keys.forEach(key => {
                            const td = document.createElement('td');
                            td.textContent = item[key] || 'N/A';
                            row.appendChild(td);
                        });
                        responseTable.appendChild(row);
                    });
                }

                // Enter display state
                loadingIndicator.style.display = 'none';
                responseSection.style.display = 'block';
            }
            submitButton.textContent = 'Return';
        } catch (error) {
            alert('Error: ' + error.message);
            loadingIndicator.style.display = 'none';
            inputDataSection.style.display = 'block';
        }
    } else {
        // Return to submission state
        responseSection.style.display = 'none';
        inputDataSection.style.display = 'block';
        submitButton.textContent = 'Submit';
        loadingIndicator.textContent = 'Loading...';
        loadingIndicator.style.display = 'none';
    }
});

// Close dropdown if clicked outside
document.addEventListener('click', (event) => {
    if (!dropdownSelected.contains(event.target) && !dropdownOptions.contains(event.target)) {
        dropdownOptions.style.display = 'none';
    }
});