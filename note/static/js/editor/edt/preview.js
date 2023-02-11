/* 
    Load preview of markdown content
    Requires markedJS
*/
/**
 * Remove anything that would submit a form
 * @param { string } parsedText string representation in HTML
 * @return { string }
 * */
function removeSubmit(parsedText) {
    const buttonExp = new RegExp(/<button.*?>\w*<\/button>/, 'g');
    const newBtns = [];
    let finalText = parsedText;

    // loop through everything and add type="button" to all buttons
    let buttonMatch = buttonExp.exec(parsedText);
    while (buttonMatch) {
        const [ match ] = buttonMatch;
        const { index } = buttonMatch;

        newBtns.push(match.search(/type/g) > -1 ? match.replace(
            /type=.*?>/,
            'type="button">'
        ): match.replace(
            '<button',
            '<button type="button"'
        ));

        const tempOutput = finalText.split('');
        tempOutput.splice(index, match.length, '$'.repeat(match.length));
        finalText = tempOutput.join('');
        buttonMatch = buttonExp.exec(finalText);
    }
    newBtns.forEach((btn) => finalText = finalText.replace(/\$+/, btn));
    return finalText;
}


/**
 * Function to transform content to markdown
 * @param { string } md "Text to transform to markdown"
 * @return { string }
 * */
function previewContent(md) {
    let parsedMd = marked.parse(
        md.replace(/^[\u200B\u200C\u200D\u200E\u200F\uFEFF]/, "")
    );
    return removeSubmit(parsedMd).replace(/<input.*?>/g, '');
}

const txt = document.getElementById('text-edit');
const preSect = document.getElementById('js-preview-window');
const pBtn = document.getElementById('preview-open');

if (pBtn) {
    pBtn.addEventListener('click', () => {
        preSect.innerHTML = previewContent(txt.value ? txt.value : '');
    });
}
