/* ============================================================
   DevCore — Blockchain Network Background Animation
   Animated nodes & connections with pulse effects
   ============================================================ */

(function() {
    'use strict';

    const canvas = document.getElementById('blockchainCanvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let width, height;
    let nodes = [];
    let animationId;
    let mouse = { x: -1000, y: -1000 };

    // Config
    const CONFIG = {
        nodeCount: 70,
        connectionDistance: 200,
        nodeSpeed: 0.3,
        nodeMinSize: 2,
        nodeMaxSize: 4,
        pulseInterval: 2000,
        mouseRadius: 250
    };

    // Resize handler
    let prevWidth = 0;
    function resize() {
        const dpr = window.devicePixelRatio || 1;
        const rect = canvas.parentElement.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) return;

        const oldWidth = width;
        width = rect.width;
        height = rect.height;
        canvas.width = width * dpr;
        canvas.height = height * dpr;
        canvas.style.width = width + 'px';
        canvas.style.height = height + 'px';
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

        // Adjust node count for mobile, or reinit if dimensions changed from 0
        const targetCount = window.innerWidth <= 768 ? 30 : CONFIG.nodeCount;
        if (nodes.length !== targetCount || !oldWidth) {
            initNodes(targetCount);
        }
    }

    // Node class
    function createNode(index, total) {
        const isGold = Math.random() < 0.15;
        return {
            x: Math.random() * width,
            y: Math.random() * height,
            vx: (Math.random() - 0.5) * CONFIG.nodeSpeed,
            vy: (Math.random() - 0.5) * CONFIG.nodeSpeed,
            size: CONFIG.nodeMinSize + Math.random() * (CONFIG.nodeMaxSize - CONFIG.nodeMinSize),
            opacity: 0.5 + Math.random() * 0.5,
            pulsePhase: Math.random() * Math.PI * 2,
            isGold: isGold,
            isBlock: Math.random() < 0.08 // Some nodes are "blocks" (squares)
        };
    }

    function initNodes(count) {
        nodes = [];
        for (let i = 0; i < count; i++) {
            nodes.push(createNode(i, count));
        }
    }

    // Pulse data traveling along connections
    let pulses = [];
    let lastPulseTime = 0;

    function spawnPulse(time) {
        if (nodes.length < 2) return;
        const fromIdx = Math.floor(Math.random() * nodes.length);
        let toIdx;
        let bestDist = Infinity;

        // Find a nearby connected node
        for (let i = 0; i < nodes.length; i++) {
            if (i === fromIdx) continue;
            const dx = nodes[i].x - nodes[fromIdx].x;
            const dy = nodes[i].y - nodes[fromIdx].y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < CONFIG.connectionDistance && dist < bestDist) {
                bestDist = dist;
                toIdx = i;
            }
        }

        if (toIdx !== undefined) {
            pulses.push({
                from: fromIdx,
                to: toIdx,
                progress: 0,
                speed: 0.008 + Math.random() * 0.012,
                isGold: Math.random() < 0.2
            });
        }
    }

    // Mouse tracking — listen on the hero section (parent of hero__bg)
    const heroSection = canvas.closest('section') || canvas.parentElement.parentElement;
    heroSection.addEventListener('mousemove', (e) => {
        const rect = canvas.getBoundingClientRect();
        mouse.x = e.clientX - rect.left;
        mouse.y = e.clientY - rect.top;
    });

    heroSection.addEventListener('mouseleave', () => {
        mouse.x = -1000;
        mouse.y = -1000;
    });

    // Animation loop
    function animate(time) {
        ctx.clearRect(0, 0, width, height);

        // Spawn pulses
        if (time - lastPulseTime > CONFIG.pulseInterval) {
            spawnPulse(time);
            lastPulseTime = time;
        }

        // Update nodes
        for (let i = 0; i < nodes.length; i++) {
            const node = nodes[i];
            node.x += node.vx;
            node.y += node.vy;

            // Bounce off edges with padding
            if (node.x < -50) node.x = width + 50;
            if (node.x > width + 50) node.x = -50;
            if (node.y < -50) node.y = height + 50;
            if (node.y > height + 50) node.y = -50;

            // Mouse repulsion
            const mdx = node.x - mouse.x;
            const mdy = node.y - mouse.y;
            const mDist = Math.sqrt(mdx * mdx + mdy * mdy);
            if (mDist < CONFIG.mouseRadius && mDist > 0) {
                const force = (CONFIG.mouseRadius - mDist) / CONFIG.mouseRadius * 0.5;
                node.vx += (mdx / mDist) * force * 0.1;
                node.vy += (mdy / mDist) * force * 0.1;
            }

            // Damping
            node.vx *= 0.999;
            node.vy *= 0.999;

            // Keep speed in range
            const speed = Math.sqrt(node.vx * node.vx + node.vy * node.vy);
            if (speed > CONFIG.nodeSpeed * 2) {
                node.vx = (node.vx / speed) * CONFIG.nodeSpeed * 2;
                node.vy = (node.vy / speed) * CONFIG.nodeSpeed * 2;
            }
            if (speed < CONFIG.nodeSpeed * 0.1) {
                node.vx += (Math.random() - 0.5) * 0.05;
                node.vy += (Math.random() - 0.5) * 0.05;
            }
        }

        // Draw connections
        for (let i = 0; i < nodes.length; i++) {
            for (let j = i + 1; j < nodes.length; j++) {
                const dx = nodes[j].x - nodes[i].x;
                const dy = nodes[j].y - nodes[i].y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < CONFIG.connectionDistance) {
                    const alpha = 1 - dist / CONFIG.connectionDistance;
                    const nearMouse = (
                        Math.sqrt((nodes[i].x - mouse.x) ** 2 + (nodes[i].y - mouse.y) ** 2) < CONFIG.mouseRadius ||
                        Math.sqrt((nodes[j].x - mouse.x) ** 2 + (nodes[j].y - mouse.y) ** 2) < CONFIG.mouseRadius
                    );

                    if (nodes[i].isGold || nodes[j].isGold) {
                        ctx.strokeStyle = `rgba(212, 168, 67, ${alpha * (nearMouse ? 0.25 : 0.12)})`;
                    } else {
                        ctx.strokeStyle = nearMouse
                            ? `rgba(0, 174, 239, ${alpha * 0.35})`
                            : `rgba(0, 174, 239, ${alpha * 0.15})`;
                    }
                    ctx.lineWidth = nearMouse ? 1.2 : 0.6;
                    ctx.beginPath();
                    ctx.moveTo(nodes[i].x, nodes[i].y);
                    ctx.lineTo(nodes[j].x, nodes[j].y);
                    ctx.stroke();
                }
            }
        }

        // Draw pulses
        for (let p = pulses.length - 1; p >= 0; p--) {
            const pulse = pulses[p];
            pulse.progress += pulse.speed;

            if (pulse.progress >= 1) {
                pulses.splice(p, 1);
                continue;
            }

            const from = nodes[pulse.from];
            const to = nodes[pulse.to];
            if (!from || !to) { pulses.splice(p, 1); continue; }

            const px = from.x + (to.x - from.x) * pulse.progress;
            const py = from.y + (to.y - from.y) * pulse.progress;
            const pulseAlpha = Math.sin(pulse.progress * Math.PI);

            const color = pulse.isGold ? `rgba(212, 168, 67, ${pulseAlpha * 0.8})` : `rgba(0, 174, 239, ${pulseAlpha * 0.8})`;

            ctx.beginPath();
            ctx.arc(px, py, 2.5, 0, Math.PI * 2);
            ctx.fillStyle = color;
            ctx.fill();

            // Pulse glow
            ctx.beginPath();
            ctx.arc(px, py, 8, 0, Math.PI * 2);
            const glowColor = pulse.isGold ? `rgba(212, 168, 67, ${pulseAlpha * 0.15})` : `rgba(0, 174, 239, ${pulseAlpha * 0.15})`;
            ctx.fillStyle = glowColor;
            ctx.fill();
        }

        // Draw nodes
        const time2 = time * 0.001;
        for (let i = 0; i < nodes.length; i++) {
            const node = nodes[i];
            const pulse = Math.sin(time2 * 2 + node.pulsePhase) * 0.3 + 0.7;
            const alpha = node.opacity * pulse;

            const nearMouse = Math.sqrt((node.x - mouse.x) ** 2 + (node.y - mouse.y) ** 2) < CONFIG.mouseRadius;
            const finalAlpha = nearMouse ? Math.min(alpha * 1.5, 1) : alpha;
            const finalSize = nearMouse ? node.size * 1.5 : node.size;

            if (node.isGold) {
                ctx.fillStyle = `rgba(212, 168, 67, ${finalAlpha})`;
            } else {
                ctx.fillStyle = `rgba(0, 174, 239, ${finalAlpha})`;
            }

            if (node.isBlock) {
                // Draw as a small rotated square (block)
                const s = finalSize * 1.2;
                ctx.save();
                ctx.translate(node.x, node.y);
                ctx.rotate(time2 * 0.5 + node.pulsePhase);
                ctx.fillRect(-s, -s, s * 2, s * 2);
                ctx.restore();
            } else {
                ctx.beginPath();
                ctx.arc(node.x, node.y, finalSize, 0, Math.PI * 2);
                ctx.fill();
            }

            // Node glow
            if (nearMouse || node.isBlock) {
                ctx.beginPath();
                ctx.arc(node.x, node.y, finalSize * 4, 0, Math.PI * 2);
                if (node.isGold) {
                    ctx.fillStyle = `rgba(212, 168, 67, ${finalAlpha * 0.08})`;
                } else {
                    ctx.fillStyle = `rgba(0, 174, 239, ${finalAlpha * 0.08})`;
                }
                ctx.fill();
            }
        }

        animationId = requestAnimationFrame(animate);
    }

    // Init
    function init() {
        resize();
        // If resize didn't get valid dimensions, retry
        if (!width || !height) {
            setTimeout(init, 100);
            return;
        }
        animationId = requestAnimationFrame(animate);
    }

    window.addEventListener('resize', resize);

    // Reduce animation on low-power / prefers-reduced-motion
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        CONFIG.nodeSpeed = 0.1;
        CONFIG.pulseInterval = 8000;
    }

    // Start after page load
    if (document.readyState === 'complete') {
        setTimeout(init, 50);
    } else {
        window.addEventListener('load', () => setTimeout(init, 50));
    }
})();
