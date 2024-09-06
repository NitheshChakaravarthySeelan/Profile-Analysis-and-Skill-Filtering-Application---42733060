let profiles = []; 

document.getElementById('create-profile').addEventListener('submit', function (e) {
    e.preventDefault();

    const name = document.getElementById('name').value.trim();
    const skills = document.getElementById('skills').value.trim().split(',');

    const profile = {
        name: name,
        skills: skills.map(skill => skill.trim().toLowerCase()) // Normalize skill input
    };
    profiles.push(profile);

    document.getElementById('name').value = '';
    document.getElementById('skills').value = '';

    console.log(profiles);
});

function filterProfiles() {
    const filterSkill = document.getElementById('filter-skill').value.trim().toLowerCase();
    const profileList = document.getElementById('profile-list');

    profileList.innerHTML = '';

    const matchingProfiles = profiles.filter(profile => 
        profile.skills.includes(filterSkill)
    );
    if (matchingProfiles.length > 0) {
        matchingProfiles.forEach(profile => {
            const li = document.createElement('li');
            li.textContent = `Name: ${profile.name}, Skills: ${profile.skills.join(', ')}`;
            profileList.appendChild(li);
        });
    } else {
        profileList.textContent = 'No matching profiles found.';
    }
}

