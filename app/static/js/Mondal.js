/* eslint-disable max-len */
// script.js

// Получаем модальное окно
var modal = document.getElementById('deleteModal');

// Получаем кнопку, которая открывает модальное окно
var deleteBtns = document.querySelectorAll('.delete-btn');

// Получаем элемент для отмены удаления
var cancelBtn = document.getElementById('cancelDelete');

// Прослушиваем клик по каждой кнопке удаления и открываем модальное окно
deleteBtns.forEach(function(btn) {
    btn.addEventListener('click', function() {
        var bookId = this.getAttribute('data-book-id'); // Предполагаем, что каждая кнопка содержит атрибут data-book-id
        var confirmDelete = document.getElementById('confirmDelete');
        confirmDelete.href = '/delete_book/' + bookId; // Устанавливаем ссылку для подтверждения удаления
        modal.style.display = 'block'; // Показываем модальное окно
    });
});

// При клике на кнопку отмены закрываем модальное окно
cancelBtn.addEventListener('click', function() {
    modal.style.display = 'none';
});

// Если пользователь кликает вне модального окна, оно закрывается
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = 'none';
    }
};