/* 
    Swith tabs around
*/

let activeLink; // hold the active link


// change up class names
function tabSwitch (newTabId, newActiveL) {
    const ct = document.getElementById(activeLink.dataset.sectionTo);
    const nt = document.getElementById(newTabId);

    if (ct && nt) {
        ct.classList.remove('editor-tab-active');
        nt.classList.add('editor-tab-active');

        if (activeLink && newActiveL) {
            activeLink.classList.remove('active');
            newActiveL.classList.add('active');
            activeLink = newActiveL;
        };
    };
};


const tabLinks = [...document.getElementsByClassName('tab-nav')];
activeLink = tabLinks.find((link) => link.classList.contains('active'));

tabLinks.forEach((link) => {
    link.addEventListener('click', (e) => {
        const cLink = e.target;
        const repTab = cLink.dataset.sectionTo;
        tabSwitch(repTab, cLink);
    });
})


/* 
    using search params load a specific tab
*/
const tabsA = [...document.getElementById('nav-tabs-sec').children].map(child => [...child.children]).flat();

// take care of similar 1st character names on tab IDs just incase
function cleanC (arr = [[]]) {
    if (arr.length < 2) {
        return arr;
    }
        
    const it = arr[0];
    const sm = arr.slice(1).filter(t => t[0] === it[0]);

    return [
        it,
        ...cleanC(sm.map((t, i) => [`${t[0]}${i+2}`, t[1]])),
        ...cleanC(arr.slice(1).filter(t => t[0] != it[0]))
    ];
};

const tabsZ = tabsA.map(a => [a.id[0], a]);

const tabs = new Map(cleanC(tabsZ));

const p = new URLSearchParams(window.location.search);

if (p.has('v') && [...tabs.keys()].includes(p.get('v'))) {
    tabs.get(p.get('v')).click();
};
