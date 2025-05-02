const logrec = document.querySelector('.logrec');
const btnPopup2 = document.querySelector('.btnLog');
const iconClose2 = document.querySelector('.icon-close2');

btnPopup2.addEventListener('click', () => {
    logrec.classList.add('active-popup');
});


iconClose2.addEventListener('click', () => {
     logrec.classList.remove('active-popup');
});

