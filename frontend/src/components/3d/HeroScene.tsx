import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';

export const HeroScene: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [webGLSupported, setWebGLSupported] = useState(true);

  useEffect(() => {
    if (!containerRef.current) return;

    // Check WebGL support
    try {
      const canvas = document.createElement('canvas');
      const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
      if (!gl) {
        setWebGLSupported(false);
        return;
      }
    } catch {
      setWebGLSupported(false);
      return;
    }

    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;

    // 1. Scene, Camera, Renderer
    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x031410, 0.035);

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    camera.position.set(0, 0.5, 6.5);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.2;
    container.appendChild(renderer.domElement);

    // 2. Lighting (Deep emerald + Neon turquoise)
    const ambientLight = new THREE.AmbientLight(0x0d382e, 1.8);
    scene.add(ambientLight);

    const cyanPoint = new THREE.PointLight(0x00f5d4, 3.5, 15);
    cyanPoint.position.set(2.5, 2.5, 3);
    scene.add(cyanPoint);

    const tealPoint = new THREE.PointLight(0x14b8a6, 2.5, 12);
    tealPoint.position.set(-3, -1.5, 2);
    scene.add(tealPoint);

    // 3. Central Floating Smartphone Mockup with glowing UI
    const phoneGroup = new THREE.Group();
    scene.add(phoneGroup);

    // Phone Body
    const bodyGeo = new THREE.BoxGeometry(2.0, 3.8, 0.15);
    const bodyMat = new THREE.MeshStandardMaterial({
      color: 0x05231c,
      metalness: 0.85,
      roughness: 0.25,
    });
    const phoneBody = new THREE.Mesh(bodyGeo, bodyMat);
    phoneGroup.add(phoneBody);

    // Glowing Edge Border
    const edgeGeo = new THREE.BoxGeometry(2.06, 3.86, 0.14);
    const edgeMat = new THREE.MeshBasicMaterial({
      color: 0x00f5d4,
      wireframe: true,
      transparent: true,
      opacity: 0.35,
    });
    const phoneEdge = new THREE.Mesh(edgeGeo, edgeMat);
    phoneGroup.add(phoneEdge);

    // Phone Screen Glass
    const screenGeo = new THREE.PlaneGeometry(1.85, 3.6);
    const screenMat = new THREE.MeshStandardMaterial({
      color: 0x031913,
      emissive: 0x063a2e,
      emissiveIntensity: 0.4,
      roughness: 0.1,
      metalness: 0.5,
    });
    const screen = new THREE.Mesh(screenGeo, screenMat);
    screen.position.z = 0.08;
    phoneGroup.add(screen);

    // Waveform rings inside phone
    const waveRingGeo = new THREE.RingGeometry(0.3, 0.35, 32);
    const waveRingMat = new THREE.MeshBasicMaterial({
      color: 0x00f5d4,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.8,
    });
    const waveRing = new THREE.Mesh(waveRingGeo, waveRingMat);
    waveRing.position.set(0, -0.4, 0.09);
    phoneGroup.add(waveRing);

    // 4. Floating 3D Healthcare Objects
    // Red/Cyan Medical Cross Shield
    const crossGroup = new THREE.Group();
    const box1 = new THREE.Mesh(
      new THREE.BoxGeometry(0.5, 0.16, 0.16),
      new THREE.MeshStandardMaterial({ color: 0x00f5d4, emissive: 0x008f7a, roughness: 0.3 })
    );
    const box2 = new THREE.Mesh(
      new THREE.BoxGeometry(0.16, 0.5, 0.16),
      new THREE.MeshStandardMaterial({ color: 0x00f5d4, emissive: 0x008f7a, roughness: 0.3 })
    );
    crossGroup.add(box1, box2);
    crossGroup.position.set(-2.4, 1.2, 0.8);
    scene.add(crossGroup);

    // Floating DNA Double Helix nodes
    const helixGroup = new THREE.Group();
    const sphereGeo = new THREE.SphereGeometry(0.08, 16, 16);
    const sphereMat = new THREE.MeshStandardMaterial({ color: 0x2dd4bf, emissive: 0x0d9488 });
    for (let i = 0; i < 14; i++) {
      const angle = i * 0.5;
      const y = (i - 7) * 0.22;
      const s1 = new THREE.Mesh(sphereGeo, sphereMat);
      s1.position.set(Math.cos(angle) * 0.4, y, Math.sin(angle) * 0.4);
      const s2 = new THREE.Mesh(sphereGeo, sphereMat);
      s2.position.set(Math.cos(angle + Math.PI) * 0.4, y, Math.sin(angle + Math.PI) * 0.4);
      helixGroup.add(s1, s2);
    }
    helixGroup.position.set(2.4, -0.6, 0.5);
    scene.add(helixGroup);

    // 5. Ambient Glowing Particles
    const particleCount = 220;
    const particleGeo = new THREE.BufferGeometry();
    const particlePositions = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount * 3; i += 3) {
      particlePositions[i] = (Math.random() - 0.5) * 12;
      particlePositions[i + 1] = (Math.random() - 0.5) * 8;
      particlePositions[i + 2] = (Math.random() - 0.5) * 6;
    }
    particleGeo.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));
    const particleMat = new THREE.PointsMaterial({
      color: 0x00f5d4,
      size: 0.05,
      transparent: true,
      opacity: 0.6,
      blending: THREE.AdditiveBlending,
    });
    const particleSystem = new THREE.Points(particleGeo, particleMat);
    scene.add(particleSystem);

    // 6. Interactive Mouse Movement
    let mouseX = 0;
    let mouseY = 0;
    let targetRotX = 0;
    let targetRotY = 0;

    const onMouseMove = (e: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      mouseX = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouseY = -(((e.clientY - rect.top) / rect.height) * 2 - 1);
    };

    window.addEventListener('mousemove', onMouseMove);

    // 7. Resize Handler
    const onResize = () => {
      if (!container) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener('resize', onResize);

    // 8. Animation Loop
    let animationFrameId: number;
    let clock = new THREE.Clock();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      const elapsedTime = clock.getElapsedTime();

      // Smooth mouse parallax
      targetRotY = mouseX * 0.35;
      targetRotX = -mouseY * 0.25;
      phoneGroup.rotation.y += (targetRotY - phoneGroup.rotation.y) * 0.05;
      phoneGroup.rotation.x += (targetRotX - phoneGroup.rotation.x) * 0.05;

      // Floating oscillation
      phoneGroup.position.y = Math.sin(elapsedTime * 1.5) * 0.12;

      // Pulsing wave ring inside phone
      const scale = 1 + Math.sin(elapsedTime * 4) * 0.25;
      waveRing.scale.set(scale, scale, 1);
      waveRingMat.opacity = 0.5 + Math.cos(elapsedTime * 4) * 0.4;

      // Rotate medical cross & helix
      crossGroup.rotation.x = elapsedTime * 0.6;
      crossGroup.rotation.y = elapsedTime * 0.8;
      crossGroup.position.y = 1.2 + Math.sin(elapsedTime * 2) * 0.15;

      helixGroup.rotation.y = elapsedTime * 0.9;
      helixGroup.position.y = -0.6 + Math.cos(elapsedTime * 1.8) * 0.15;

      // Slow particle rotation
      particleSystem.rotation.y = elapsedTime * 0.04;

      renderer.render(scene, camera);
    };

    animate();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('resize', onResize);
      renderer.dispose();
      if (container && renderer.domElement) {
        container.removeChild(renderer.domElement);
      }
    };
  }, []);

  if (!webGLSupported) {
    return (
      <div className="w-full h-full flex items-center justify-center p-6 bg-gradient-to-br from-emerald-950/40 to-teal-900/30 rounded-3xl border border-teal-500/20 backdrop-blur-xl">
        <div className="text-center">
          <div className="w-24 h-24 mx-auto mb-4 rounded-full bg-teal-500/20 border-2 border-teal-400 flex items-center justify-center text-teal-300 animate-pulse">
            <span className="text-4xl">🎙️</span>
          </div>
          <h3 className="text-xl font-bold text-teal-200">ASHA-VAANI 3D Assistant</h3>
          <p className="text-sm text-teal-400/80 mt-1">High-performance voice documentation interface</p>
        </div>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="w-full h-full min-h-[460px] lg:min-h-[580px] relative cursor-grab active:cursor-grabbing"
    />
  );
};
