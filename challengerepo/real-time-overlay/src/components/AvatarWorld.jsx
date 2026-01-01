import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Stars, Grid, Text } from '@react-three/drei';
import { useRef, useState, useMemo } from 'react';

function RotatingGrid() {
    const gridRef = useRef();
    useFrame((state, delta) => {
        if (gridRef.current) {
            gridRef.current.rotation.y += delta * 0.05;
        }
    });
    return (
        <group ref={gridRef} rotation={[-Math.PI / 4, 0, 0]}> {/* Angled grid for impact */}
            <Grid
                args={[100, 100]}
                cellSize={1}
                cellThickness={0.5}
                cellColor="#00f0ff"
                sectionSize={5}
                sectionThickness={1}
                sectionColor="#ff003c"
                fadeDistance={50}
            />
        </group>
    );
}

function FloatingCube() {
    const meshRef = useRef();
    useFrame((state, delta) => {
        meshRef.current.rotation.x += delta * 0.2;
        meshRef.current.rotation.y += delta * 0.2;
    });

    return (
        <mesh ref={meshRef} position={[0, 2, 0]}>
            <boxGeometry args={[2, 2, 2]} />
            <meshStandardMaterial wireframe color="white" />
        </mesh>
    );
}

// Floating sphere with hover animation
function FloatingSphere() {
    const meshRef = useRef();
    useFrame((state) => {
        meshRef.current.position.y = Math.sin(state.clock.elapsedTime) * 0.5 + 3;
        meshRef.current.rotation.z += 0.01;
    });
    return (
        <mesh ref={meshRef} position={[4, 3, 0]}>
            <sphereGeometry args={[0.8, 32, 32]} />
            <meshStandardMaterial color="#00ff88" emissive="#00ff88" emissiveIntensity={0.3} />
        </mesh>
    );
}

// Interactive torus - click to change color
function InteractiveTorus() {
    const [color, setColor] = useState('#ff003c');
    const [hovered, setHovered] = useState(false);
    const meshRef = useRef();
    
    useFrame((state, delta) => {
        meshRef.current.rotation.x += delta * 0.3;
        meshRef.current.rotation.y += delta * 0.2;
    });
    
    return (
        <mesh 
            ref={meshRef}
            position={[-4, 2, 0]} 
            onClick={() => setColor(color === '#ff003c' ? '#00f0ff' : '#ff003c')}
            onPointerOver={() => setHovered(true)}
            onPointerOut={() => setHovered(false)}
            scale={hovered ? 1.2 : 1}
        >
            <torusGeometry args={[1, 0.3, 16, 50]} />
            <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.2} />
        </mesh>
    );
}

// Floating particles
function Particles() {
    const count = 500;
    const particlesRef = useRef();
    
    const positions = useMemo(() => {
        const pos = new Float32Array(count * 3);
        for (let i = 0; i < count * 3; i++) {
            pos[i] = (Math.random() - 0.5) * 30;
        }
        return pos;
    }, []);
    
    useFrame((state) => {
        if (particlesRef.current) {
            particlesRef.current.rotation.y = state.clock.elapsedTime * 0.02;
        }
    });
    
    return (
        <points ref={particlesRef}>
            <bufferGeometry>
                <bufferAttribute attach="attributes-position" count={count} array={positions} itemSize={3} />
            </bufferGeometry>
            <pointsMaterial size={0.08} color="#00f0ff" transparent opacity={0.6} sizeAttenuation />
        </points>
    );
}

// Floating text label
function FloatingText() {
    const textRef = useRef();
    useFrame((state) => {
        if (textRef.current) {
            textRef.current.position.y = 6 + Math.sin(state.clock.elapsedTime * 0.5) * 0.3;
        }
    });
    return (
        <Text 
            ref={textRef}
            position={[0, 6, 0]} 
            fontSize={0.8} 
            color="#00f0ff" 
            anchorX="center"
            font={undefined}
        >
            NETWORKBUSTER
        </Text>
    );
}

// Orbiting ring
function OrbitingRing() {
    const ringRef = useRef();
    useFrame((state) => {
        ringRef.current.rotation.z = state.clock.elapsedTime * 0.5;
        ringRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.3) * 0.3;
    });
    return (
        <mesh ref={ringRef} position={[0, 2, 0]}>
            <torusGeometry args={[3.5, 0.05, 16, 100]} />
            <meshStandardMaterial color="#ff003c" emissive="#ff003c" emissiveIntensity={0.5} />
        </mesh>
    );
}

// Pulsing core
function PulsingCore() {
    const coreRef = useRef();
    useFrame((state) => {
        const scale = 1 + Math.sin(state.clock.elapsedTime * 2) * 0.1;
        coreRef.current.scale.set(scale, scale, scale);
    });
    return (
        <mesh ref={coreRef} position={[0, 2, 0]}>
            <icosahedronGeometry args={[0.5, 1]} />
            <meshStandardMaterial 
                color="#ffffff" 
                emissive="#00f0ff" 
                emissiveIntensity={1} 
                wireframe 
            />
        </mesh>
    );
}


export default function AvatarWorld() {
    return (
        <div className="absolute inset-0 -z-10">
            <Canvas camera={{ position: [0, 5, 12], fov: 60 }}>
                <fog attach="fog" args={['#050505', 10, 60]} />
                <ambientLight intensity={0.5} />
                <pointLight position={[10, 10, 10]} intensity={1} color="#00f0ff" />
                <pointLight position={[-10, -10, -10]} intensity={1} color="#ff003c" />
                <pointLight position={[0, 5, 0]} intensity={0.5} color="#ffffff" />

                <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
                <RotatingGrid />
                <FloatingCube />
                <FloatingSphere />
                <InteractiveTorus />
                <Particles />
                <FloatingText />
                <OrbitingRing />
                <PulsingCore />

                <OrbitControls autoRotate autoRotateSpeed={0.5} enableZoom={true} maxDistance={30} minDistance={5} />
            </Canvas>
        </div>
    );
}
