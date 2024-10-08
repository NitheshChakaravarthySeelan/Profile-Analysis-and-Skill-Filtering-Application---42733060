document.addEventListener('DOMContentLoaded', function () {
    const filterInput = document.getElementById('filterInput');
    const candidateList = document.querySelectorAll('.candidate-list li');

    filterInput.addEventListener('input', function () {
        const query = filterInput.value.toLowerCase();

        candidateList.forEach(candidate => {
            const candidateText = candidate.textContent.toLowerCase();
            if (candidateText.includes(query)) {
                candidate.style.display = 'block';
            } else {
                candidate.style.display = 'none';
            }
        });
    });
});
