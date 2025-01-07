const korzina= document.getElementById ('korzina');
const cancel= document.getElementById('cancel')
const appear =document.getElementById("shop-js");

korzina.addEventListener('click', () => {
    appear.showModal();

});
cancel.addEventListener('click',() => {
    appear.close();
});
const action = document. getElementById('danya')
const poisk= document.getElementById('ksysha')


poisk.addEventListener('focus', () => {
  action.style.display = 'block';
  console.log(5);
});

poisk.addEventListener('blur', () => {
  // Важный момент!  Удерживаем popup до тех пор, пока пользователь не кликнет
  // вне зоны действия popup
  // ... (Ваш код, например, проверка на клик вне div)
  action.style.display = 'none';
  console.log(5);
});
poisk.oninput = function() {
    let value = this.value.trim().toLowerCase();
    let list = document.querySelectorAll('.list li')
    if (value === '') {
        list.forEach(elem => elem.classList.remove('hide')); // Убираем класс при пустом вводе
        return; // Выходим из функции, если строка пустая
    }

    list.forEach(elem => {
        const text = elem.textContent.toLowerCase(); // Переводим в нижний регистр для сравнения
        if (text.indexOf(value) === -1) {
            elem.classList.add('hide');
        } else {
            elem.classList.remove('hide'); // Важно: убираем класс, если совпадение есть
        }
    })
};








