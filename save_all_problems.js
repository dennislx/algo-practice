const fs = require('fs');

fetch('https://leetcode.com/api/problems/all/')
    .then(response => response.json())
    .then(data => {
        const problems = {};
        data.stat_status_pairs.forEach(problem => {
            const paddedId = problem.stat.frontend_question_id.toString().padStart(4, '0');
            problems[paddedId] = problem.stat.question__title_slug;
        });
        const jsonData = JSON.stringify(problems, null, 2);
        fs.writeFileSync('scripts/config/problems.json', jsonData);
    })
    .catch(error => console.error(error));