document.addEventListener('DOMContentLoaded', () => {
    // Exemplo de interação no botão de login
    const loginBtn = document.querySelector('.btn-ifpi-green');
    
    loginBtn.addEventListener('click', (e) => {
        // Simulação de clique/loading
        const originalContent = loginBtn.innerHTML;
        loginBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Autenticando...`;
        
        // Em um sistema real, aqui aconteceria o redirecionamento para o OAuth/SAML institucional
        setTimeout(() => {
            console.log("Redirecionando para login institucional...");
            // loginBtn.innerHTML = originalContent; // Reset se necessário
        }, 2000);
    });

    // Scroll suave para links internos (se houver)
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
});