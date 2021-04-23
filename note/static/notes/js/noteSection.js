// create new sections on the nav
function navPainter (items = []) {
    const noteNav = document.getElementById('note-nav-drop-down');
    const distances = new Map (Array.from(Array(6), (x, i) => [`H${1+i}`, i*15]));

    const htmlText = items.map((item, i) => {
        let navText = `<a class="dropdown-item" href="${item.link}" style="padding-left: ${distances.get(item.tag)+3}px;">${item.name}</a>`;

        if (i > 0) {
            navText = '<div class="dropdown-divider"></div>' + navText;
        };

        return navText;
    });

    noteNav.innerHTML = htmlText.join(' ');
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
        document.getElementById('navbarDropdown').disabled = true;
    };
}