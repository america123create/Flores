// ==========================================
// JavaScript principal para funcionalidad general
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    
    // ==========================================
    // Auto-cerrar mensajes flash después de 5 segundos
    // ==========================================
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            message.style.animation = 'slideOutRight 0.4s ease';
            setTimeout(function() {
                message.remove();
            }, 400);
        }, 5000);
    });
    
    // ==========================================
    // Animación de entrada para tarjetas
    // ==========================================
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observar elementos animables
    const animatableElements = document.querySelectorAll('.feature-card, .dashboard-card');
    animatableElements.forEach(function(element) {
        observer.observe(element);
    });
    
    // ==========================================
    // Efecto parallax suave en el fondo
    // ==========================================
    let ticking = false;
    
    window.addEventListener('scroll', function() {
        if (!ticking) {
            window.requestAnimationFrame(function() {
                const scrolled = window.pageYOffset;
                const bgDecoration = document.querySelector('.bg-decoration');
                
                if (bgDecoration) {
                    bgDecoration.style.transform = `translateY(${scrolled * 0.3}px)`;
                }
                
                ticking = false;
            });
            
            ticking = true;
        }
    });
    
    // ==========================================
    // Animación del logo
    // ==========================================
    const logoIcon = document.querySelector('.logo-icon');
    if (logoIcon) {
        logoIcon.addEventListener('mouseenter', function() {
            this.style.animationPlayState = 'paused';
        });
        
        logoIcon.addEventListener('mouseleave', function() {
            this.style.animationPlayState = 'running';
        });
    }
    
    // ==========================================
    // Smooth scroll para links internos
    // ==========================================
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
    
    // ==========================================
    // Efecto hover en tarjetas de características
    // ==========================================
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(function(card) {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    // ==========================================
    // Animación de contador (para estadísticas futuras)
    // ==========================================
    function animateCounter(element, target, duration) {
        let start = 0;
        const increment = target / (duration / 16);
        
        const timer = setInterval(function() {
            start += increment;
            if (start >= target) {
                element.textContent = target;
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(start);
            }
        }, 16);
    }
    
    // ==========================================
    // Formulario: Prevenir envío con Enter en campos específicos
    // ==========================================
    const formInputs = document.querySelectorAll('.form-input:not([type="submit"])');
    formInputs.forEach(function(input) {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && this.type !== 'submit') {
                e.preventDefault();
                // Enfocar el siguiente campo
                const form = this.closest('form');
                const inputs = Array.from(form.querySelectorAll('input, button, select, textarea'));
                const index = inputs.indexOf(this);
                if (index < inputs.length - 1) {
                    inputs[index + 1].focus();
                }
            }
        });
    });
    
    // ==========================================
    // Toggle switches animados
    // ==========================================
    const toggleSwitches = document.querySelectorAll('.toggle-switch input');
    toggleSwitches.forEach(function(toggle) {
        toggle.addEventListener('change', function() {
            const slider = this.nextElementSibling;
            if (this.checked) {
                slider.style.transform = 'scale(1.1)';
                setTimeout(function() {
                    slider.style.transform = 'scale(1)';
                }, 200);
            }
        });
    });
    
    // ==========================================
    // Efecto de escritura para títulos (opcional)
    // ==========================================
    function typeWriter(element, text, speed) {
        let i = 0;
        element.textContent = '';
        
        function type() {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
                setTimeout(type, speed);
            }
        }
        
        type();
    }
    
    // ==========================================
    // Detectar modo oscuro del sistema (para futuras implementaciones)
        // ==========================================
    /* if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        // El usuario prefiere modo oscuro
        // Aquí se podría implementar lógica para cambiar el tema
        console.log('Modo oscuro detectado');
    } */
    
    // ==========================================
    // Prevenir doble envío de formularios
    // ==========================================
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton && !submitButton.disabled) {
                // Deshabilitar el botón temporalmente
                submitButton.disabled = true;
                submitButton.style.opacity = '0.5';
                
                // Re-habilitar después de 3 segundos por si hay un error
                setTimeout(function() {
                    submitButton.disabled = false;
                    submitButton.style.opacity = '1';
                }, 3000);
            }
        });
    });
    
    // ==========================================
    // Animación de carga inicial
    // ==========================================
    document.body.style.opacity = '0';
    setTimeout(function() {
        document.body.style.transition = 'opacity 0.5s ease';
        document.body.style.opacity = '1';
    }, 100);
    
    // ==========================================
    // Logs de desarrollo (comentar en producción)
    // ==========================================
    //console.log('%c¡Bienvenido a WebApp! 🚀', 'color: #ff6b6b; font-size: 20px; font-weight: bold;');
    //console.log('%cSitio web desarrollado con Flask y diseño moderno', 'color: #4ecdc4; font-size: 14px;');
});

// ==========================================
// Animación para el slideOutRight
// ==========================================
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);