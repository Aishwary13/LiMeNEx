window.onload = function() {
    setTimeout(function() {
        const container = document.getElementById('network-animation');
        
        if (container) {
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);

            const renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(container.clientWidth, container.clientHeight);
            container.appendChild(renderer.domElement);

            const geometry = new THREE.SphereGeometry(0.5, 32, 32);
            const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
            const sphere = new THREE.Mesh(geometry, material);
            scene.add(sphere);

            camera.position.z = 5;

            const animate = function() {
                requestAnimationFrame(animate);

                sphere.rotation.x += 0.01;
                sphere.rotation.y += 0.01;

                renderer.render(scene, camera);
            };

            animate();
        } else {
            console.error("Element with ID 'network-animation' not found.");
        }
    }, 500);  // Adjust the delay as needed
};
