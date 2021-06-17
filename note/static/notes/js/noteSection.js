// create new sections on the nav
function navPainter (items = []) {
    const noteNav = document.getElementById('note-nav-drop-down');
    const distances = new Map (Array.from(Array(6), (x, i) => [`H${1+i}`, i*15]));
    const sectionClick = new Event('sectionClick');
    let ac;

    noteNav.innerHTML = '';
    items.forEach((item) => {
        const nav = document.createElement('a');
        nav.className = "dropdown-item";
        nav.href = item.link;
        nav.style.paddingLeft = `${distances.get(item.tag) + 3}px`;
        noteNav.appendChild(nav);
        nav.innerText = item.name;
        nav.addEventListener('sectionClick', (event_) => {
            ac? ac.classList.remove('active'): void 0;
            event_.target.classList.add('active');
            ac = event_.target;
        });
        nav.addEventListener('click', () => nav.dispatchEvent(sectionClick));
        const divider = document.createElement('div');
        divider.className = "dropdown-divider stupid-divider";
        noteNav.appendChild(divider);
    });
};


// look for headers on the Note
function headerScout (parent) {
    const headers = ['H1', 'H2', 'H3', 'H4', 'H5', 'H6'];
    const children = Array.from(parent.children);
    const heads = children.filter((child) => headers.includes(child.tagName));

    for (let child of children) {
        if (child.childElementCount > 0) {
            heads.concat(headerScout(child));
        };
    };
    return heads;
};


// main function to load nav
function loadNoteNav (noteDiv) {
    const headers = headerScout(noteDiv).map((head) => ({
        name: head.innerText,
        link: `#${head.id}`,
        tag: head.tagName
    }));

    if (headers.length > 0) {
        navPainter(headers);
    } else {
        document.getElementById('dropdownMenuLink').disabled = true;
        document.getElementById('note-sections-nav').classList.remove('sticky-top')
    };
}


