function revelarNaScroll() {
    var contents = document.querySelectorAll('.content');

    for (var i = 0; i < contents.length; i++) {
        var windowHeight = window.innerHeight;
        var elementTop = contents[i].getBoundingClientRect().top;
        var elementVisible = 150; // Quantos pixels do elemento devem estar visíveis para iniciar a animação

        if (elementTop < windowHeight - elementVisible) {
            contents[i].classList.add('visible');
        } else {
            contents[i].classList.remove('visible');
        }
    }
}





window.addEventListener('scroll', revelarNaScroll);

