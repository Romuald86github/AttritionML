document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('prediction-form');
    const resultDiv = document.getElementById('prediction-result');

    form.addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = {
            'DailyRate': document.getElementById('daily-rate').value,
            'DistanceFromHome': document.getElementById('distance-from-home').value,
            'EnvironmentSatisfaction': document.getElementById('environment-satisfaction').value,
            'JobInvolvement': document.getElementById('job-involvement').value,
            'JobSatisfaction': document.getElementById('job-satisfaction').value,
            'MaritalStatus': document.getElementById('marital-status').value,
            'NumCompaniesWorked': document.getElementById('num-companies-worked').value,
            'OverTime': document.getElementById('overtime').value,
            'StockOptionLevel': document.getElementById('stock-option-level').value,
            'TotalWorkingYears': document.getElementById('total-working-years').value,
            'TrainingTimesLastYear': document.getElementById('training-times-last-year').value,
            'WorkLifeBalance': document.getElementById('work-life-balance').value,
            'YearsAtCompany': document.getElementById('years-at-company').value
        };

        fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.prediction === 0) {
                resultDiv.textContent = 'The employee is not likely to leave the company.';
            } else {
                resultDiv.textContent = 'The employee is likely to leave the company.';
            }
        })
        .catch(error => {
            resultDiv.textContent = 'Error making prediction: ' + error;
        });
    });
});