
/**
 * Submits the language form with the
 * desired language code.
 * @param {String} languageCode 
 */
function submitLanguageForm(languageCode){
    document.getElementById('language-input').value = languageCode;
    document.getElementById('language-form').submit();
}