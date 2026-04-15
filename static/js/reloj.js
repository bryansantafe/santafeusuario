// static/core/js/reloj.js

function actualizarReloj() {
    // Buscamos el elemento donde se mostrará la hora
    const elementoReloj = document.getElementById('reloj-vivo');

    // Si no encuentra el elemento en la página actual, detenemos la función
    if (!elementoReloj) return;

    const ahora = new Date();
    let horas = ahora.getHours();
    let minutos = ahora.getMinutes();
    let ampm = horas >= 12 ? 'PM' : 'AM';

    horas = horas % 12;
    horas = horas ? horas : 12; // la hora '0' debe ser '12'
    minutos = minutos < 10 ? '0' + minutos : minutos; // agregar un cero si es menor a 10

    // Imprimimos la hora en el HTML
    elementoReloj.textContent = `${horas}:${minutos} ${ampm}`;
}

// Escuchamos a que el HTML termine de cargar antes de encender el reloj
document.addEventListener('DOMContentLoaded', () => {
    actualizarReloj();
    setInterval(actualizarReloj, 1000); // Actualizar cada 1 segundo
});