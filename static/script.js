// خلفية الكريات
const canvas = document.getElementById('backgroundCanvas');
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const particles = [];
const particleCount = 30;

class Particle {
    constructor() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.radius = 5;
        this.speedX = (Math.random() - 0.5) * 2;
        this.speedY = (Math.random() - 0.5) * 2;
    }

    draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fillStyle = '#ffeb3b';
        ctx.fill();
    }

    update() {
        this.x += this.speedX;
        this.y += this.speedY;

        if (this.x < 0 || this.x > canvas.width) this.speedX *= -1;
        if (this.y < 0 || this.y > canvas.height) this.speedY *= -1;
    }
}

for (let i = 0; i < particleCount; i++) {
    particles.push(new Particle());
}

function connectParticles() {
    for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
            const dx = particles[i].x - particles[j].x;
            const dy = particles[i].y - particles[j].y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < 100) {
                ctx.beginPath();
                ctx.strokeStyle = '#ffeb3b';
                ctx.lineWidth = 1;
                ctx.moveTo(particles[i].x, particles[i].y);
                ctx.lineTo(particles[j].x, particles[j].y);
                ctx.stroke();
            }
        }
    }
}

function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(particle => {
        particle.update();
        particle.draw();
    });
    connectParticles();
    requestAnimationFrame(animate);
}

animate();

// وظيفة تحميل الفيديو
function downloadVideo() {
    const url = document.getElementById('videoUrl').value;
    const status = document.getElementById('status');
    status.textContent = 'جاري المعالجة...';

    fetch('/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const downloadLink = document.createElement('a');
            downloadLink.href = data.download_link;
            downloadLink.textContent = 'اضغط هنا لتحميل الفيديو';
            downloadLink.style.color = '#ffeb3b';
            status.innerHTML = 'تم التحميل! ';
            status.appendChild(downloadLink);
        } else {
            status.textContent = 'حدث خطأ: ' + data.error;
        }
    })
    .catch(err => {
        status.textContent = 'خطأ في الاتصال بالخادم';
    });
}