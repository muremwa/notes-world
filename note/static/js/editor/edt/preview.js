/* 
    Load preview of markdown content
    Requires markedJS
*/

const txt = document.getElementById('text-edit');
const preSect = document.getElementById('js-preview-window');

const previewContent = (md = txt.value? txt.value: '', sect = preSect) => {
    sect.innerHTML = marked(md);
};

const pBtn = document.getElementById('preview-open');

if (pBtn) {
    pBtn.addEventListener('click', () => previewContent());
};
