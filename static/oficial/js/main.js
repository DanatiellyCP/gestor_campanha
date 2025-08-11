document.addEventListener("DOMContentLoaded", function() {

    // --- 1. CARREGAMENTO DINÂMICO DO HEADER ---
    const loadHeader = () => {
        const headerPlaceholder = document.getElementById("header-placeholder");
        if (headerPlaceholder) {
            fetch('_header.html')
                .then(response => {
                    if (!response.ok) throw new Error("Header não encontrado");
                    return response.text();
                })
                .then(data => {
                    headerPlaceholder.innerHTML = data;

                    // --- FUNÇÕES QUE DEPENDEM DO HEADER CARREGADO ---

                    // A. Efeito de scroll no header
                    const header = document.querySelector('.main-header');
                    if (header) {
                        window.addEventListener('scroll', () => {
                            if (window.scrollY > 50) {
                                header.classList.add('scrolled');
                            } else {
                                header.classList.remove('scrolled');
                            }
                        });
                    }

                    // B. Menu Hamburger para mobile (CORRIGIDO)
                    const hamburger = document.querySelector('.hamburger-menu');
                    const menuWrapper = document.querySelector('.header-menu-wrapper');
                    if (hamburger && menuWrapper) {
                        hamburger.addEventListener('click', () => {
                            menuWrapper.classList.toggle('active');
                            hamburger.classList.toggle('active');
                        });
                    }
                })
                .catch(error => console.error('Erro ao carregar o header:', error));
        }
    };

    // --- 2. FUNCIONALIDADE DO ACORDEÃO (Sorteios / FAQ) ---
    const accordionItems = document.querySelectorAll('.accordion-item');
    if (accordionItems.length > 0) {
        accordionItems.forEach(item => {
            const accordionHeader = item.querySelector('.accordion-header');
            if (accordionHeader) {
                accordionHeader.addEventListener('click', () => {
                    item.classList.toggle('active');
                    const content = item.querySelector('.accordion-content');
                    if (content.style.maxHeight) {
                        content.style.maxHeight = null;
                    } else {
                        content.style.maxHeight = content.scrollHeight + "px";
                    }
                });
            }
        });
    }

    // --- 3. FUNCIONALIDADE DA LISTA DE PRODUTOS (Página Como Participar) ---
    const toggleProdutosBtn = document.querySelector('.toggle-produtos-btn');
    if (toggleProdutosBtn) {
        toggleProdutosBtn.addEventListener('click', () => {
            const listaProdutos = document.querySelector('#lista-de-produtos');
            toggleProdutosBtn.classList.toggle('active');
            
            const icon = toggleProdutosBtn.querySelector('.toggle-icon');
            const isExpanded = toggleProdutosBtn.getAttribute('aria-expanded') === 'true';

            if (isExpanded) {
                toggleProdutosBtn.setAttribute('aria-expanded', 'false');
                if (icon) icon.textContent = '+';
            } else {
                toggleProdutosBtn.setAttribute('aria-expanded', 'true');
                if (icon) icon.textContent = '–';
            }

            if (listaProdutos.style.maxHeight) {
                listaProdutos.style.maxHeight = null;
            } else {
                listaProdutos.style.maxHeight = listaProdutos.scrollHeight + "px";
            }
        });
    }
    
    // --- 4. LÓGICA DO BANNER DE COOKIES ---
    const handleCookieConsent = () => {
        if (document.cookie.includes('user_consent=true')) {
            return;
        }
        const bannerHTML = `
            <div class="cookie-consent-banner" id="cookie-banner">
                <p class="cookie-consent-text">
                    Utilizamos cookies para otimizar sua experiência em nosso site. Ao continuar a navegação, você concorda com a nossa <a href="#">Política de Privacidade</a>.
                </p>
                <button class="cookie-consent-button" id="accept-cookies-btn">ACEITAR E FECHAR</button>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', bannerHTML);
        const banner = document.getElementById('cookie-banner');
        setTimeout(() => {
            banner.classList.add('active');
        }, 100);
        document.getElementById('accept-cookies-btn').addEventListener('click', () => {
            const expirationDate = new Date();
            expirationDate.setFullYear(expirationDate.getFullYear() + 1);
            document.cookie = `user_consent=true; path=/; expires=${expirationDate.toUTCString()}; SameSite=Lax`;
            banner.classList.remove('active');
            setTimeout(() => {
                banner.remove();
            }, 500);
        });
    };

    // --- 5. BOTÃO FLUTUANTE DO WHATSAPP ---
    const createWhatsAppButton = () => {
        const phoneNumber = '5511999999999';
        const whatsappLink = document.createElement('a');
        whatsappLink.href = `https://wa.me/${phoneNumber}`;
        whatsappLink.className = 'whatsapp-flutuante';
        whatsappLink.target = '_blank';
        whatsappLink.rel = 'noopener noreferrer';
        whatsappLink.setAttribute('aria-label', 'Fale Conosco pelo WhatsApp');
        const whatsappIcon = document.createElement('img');
        whatsappIcon.src = 'static/oficial/images/whatsapp-icon.png';
        whatsappIcon.alt = 'Ícone do WhatsApp';
        whatsappLink.appendChild(whatsappIcon);
        document.body.appendChild(whatsappLink);
    };

    // --- CHAMADAS INICIAIS ---
    loadHeader();
    handleCookieConsent();
    // createWhatsAppButton();

});