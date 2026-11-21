import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

interface Microphone3DProps {
  isListening: boolean;
  isProcessing: boolean;
  isSpeaking: boolean;
  audioLevel?: number; // 0.0 to 1.0 from Web Audio Analyser
}

export const Microphone3D: React.FC<Microphone3DProps> = ({
  isListening,
  isProcessing,
  isSpeaking,
  audioLevel = 0,
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const audioLevelRef = useRef(audioLevel);
  const stateRef = useRef({ isListening, isProcessing, isSpeaking });

  useEffect(() => {
    audioLevelRef.current = audioLevel;
  }, [audioLevel]);

  useEffect(() => {
    stateRef.current = { isListening, isProcessing, isSpeaking };
  }, [isListening, isProcessing, isSpeaking]);

  useEffect(() => {
    if (!mountRef.current) return;
    const container = mountRef.current;
    const width = container.clientWidth || 280;
    const height = container.clientHeight || 280;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 50);
    camera.position.set(0, 0, 4.5);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // Ambient & Rim Lights
    const ambientLight = new THREE.AmbientLight(0x0a3328, 2.5);
    scene.add(ambientLight);

    const pointLight = new THREE.PointLight(0x00f5d4, 3, 10);
    pointLight.position.set(2, 2, 3);
    scene.add(pointLight);

    const backLight = new THREE.PointLight(0x14b8a6, 2, 8);
    backLight.position.set(-2, -2, -2);
    scene.add(backLight);

    // Microphone Model Group
    const micGroup = new THREE.Group();
    scene.add(micGroup);

    // 1. Microphone Capsule (Head)
    const headGeo = new THREE.SphereGeometry(0.65, 32, 24);
    const headMat = new THREE.MeshStandardMaterial({
      color: 0x052a21,
      metalness: 0.9,
      roughness: 0.2,
      wireframe: true,
    });
    const head = new THREE.Mesh(headGeo, headMat);
    head.position.y = 0.45;
    micGroup.add(head);

    // Inner glowing core
    const coreGeo = new THREE.SphereGeometry(0.5, 24, 24);
    const coreMat = new THREE.MeshBasicMaterial({
      color: 0x00f5d4,
      transparent: true,
      opacity: 0.4,
    });
    const core = new THREE.Mesh(coreGeo, coreMat);
    core.position.y = 0.45;
    micGroup.add(core);

    // 2. Microphone Handle
    const handleGeo = new THREE.CylinderGeometry(0.28, 0.22, 1.3, 32);
    const handleMat = new THREE.MeshStandardMaterial({
      color: 0x041914,
      metalness: 0.85,
      roughness: 0.35,
    });
    const handle = new THREE.Mesh(handleGeo, handleMat);
    handle.position.y = -0.55;
    micGroup.add(handle);

    // 3. Audio Reactive Outer Shock Ring
    const ringGeo = new THREE.TorusGeometry(1.05, 0.03, 16, 64);
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0x00f5d4,
      transparent: true,
      opacity: 0.6,
    });
    const shockRing = new THREE.Mesh(ringGeo, ringMat);
    shockRing.rotation.x = Math.PI / 2;
    shockRing.position.y = 0.45;
    micGroup.add(shockRing);

    // Second orbital halo
    const haloGeo = new THREE.TorusGeometry(1.35, 0.02, 16, 64);
    const haloMat = new THREE.MeshBasicMaterial({
      color: 0x14b8a6,
      transparent: true,
      opacity: 0.3,
    });
    const halo = new THREE.Mesh(haloGeo, haloMat);
    halo.position.y = 0.45;
    micGroup.add(halo);

    let animationFrameId: number;
    let clock = new THREE.Clock();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      const elapsed = clock.getElapsedTime();
      const currentAudio = audioLevelRef.current;
      const { isListening: listening, isProcessing: processing, isSpeaking: speaking } = stateRef.current;

      // Base idle rotation
      micGroup.rotation.y = elapsed * 0.5;

      // Color and pulse reactivity
      if (listening) {
        // Neon cyan audio pulse
        pointLight.color.setHex(0x00f5d4);
        coreMat.color.setHex(0x00f5d4);
        coreMat.opacity = 0.4 + currentAudio * 0.6;
        
        const audioScale = 1 + currentAudio * 0.45;
        shockRing.scale.set(audioScale, audioScale, audioScale);
        shockRing.rotation.z = elapsed * 2;
        ringMat.color.setHex(0x00f5d4);
        ringMat.opacity = 0.7 + currentAudio * 0.3;

        halo.scale.set(1 + currentAudio * 0.6, 1 + currentAudio * 0.6, 1);
        halo.rotation.x = elapsed * 1.5;
      } else if (processing) {
        // Amber/gold fast spin
        pointLight.color.setHex(0xf59e0b);
        coreMat.color.setHex(0xf59e0b);
        coreMat.opacity = 0.5 + Math.sin(elapsed * 8) * 0.3;

        shockRing.rotation.z = elapsed * 5;
        ringMat.color.setHex(0xf59e0b);
        halo.rotation.y = elapsed * 4;
      } else if (speaking) {
        // Deep emerald speaking pulse
        pointLight.color.setHex(0x10b981);
        coreMat.color.setHex(0x10b981);
        const speakPulse = 1 + Math.sin(elapsed * 6) * 0.2;
        shockRing.scale.set(speakPulse, speakPulse, speakPulse);
        ringMat.color.setHex(0x10b981);
      } else {
        // Idle standby
        pointLight.color.setHex(0x0d9488);
        coreMat.color.setHex(0x0d9488);
        coreMat.opacity = 0.2;
        shockRing.scale.set(1, 1, 1);
        ringMat.color.setHex(0x0d9488);
        ringMat.opacity = 0.25;
      }

      renderer.render(scene, camera);
    };

    animate();

    const onResize = () => {
      if (!container) return;
      const w = container.clientWidth || 280;
      const h = container.clientHeight || 280;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };

    window.addEventListener('resize', onResize);

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', onResize);
      renderer.dispose();
      if (container && renderer.domElement) {
        container.removeChild(renderer.domElement);
      }
    };
  }, []);

  return (
    <div
      ref={mountRef}
      className="w-full h-full min-h-[260px] flex items-center justify-center relative pointer-events-none"
    />
  );
};
