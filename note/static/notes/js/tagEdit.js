// paint tags
function paintTagsPreview (names = []) {
    const tagsList = document.getElementById('tags-list');
    // clear our previous tags
    tagsList.innerHTML = '';
    const home = document.getElementById('tags-view');
    home.classList.add('highlight');

    setTimeout(() => home.classList.remove('highlight'), 600);

    names.forEach((name) => {
        const tag = document.createElement('li');
        tag.className = 'tags-list-tag';
        tag.innerText = name;
        tagsList.appendChild(tag);
    });

};


// fetch tags
function fetchTagsforPreview () {
    const tagsHome = document.getElementById('tags-select');
    return Array.from(tagsHome).filter((tag) => tag.selected === true).map((tag) => tag.innerText);
}


// attach listener
document.getElementById('preview-tags').addEventListener('click', (e) => {
    e.preventDefault();
    paintTagsPreview(fetchTagsforPreview());
});
