import { BackgroundGradientAnimation } from "@/components/atoms/BackgroundGradientAnimation/BackgroundGradientAnimation";

export default function Hero() {
    return (
        <BackgroundGradientAnimation
            gradientBackgroundStart="rgb(108, 0, 162)"
            gradientBackgroundEnd="rgb(0, 17, 82)"
            firstColor="18, 113, 255"
            secondColor="200, 50, 50"
            thirdColor="255, 160, 122"
            fourthColor="221, 74, 255"
            fifthColor="100, 220, 255"
            pointerColor="140, 100, 255"
            blendingValue="hard-light"
            interactive={true}
        >
            <div className="absolute z-50 inset-0 flex items-center justify-center text-white font-bold px-4 pointer-events-none text-3xl text-center md:text-4xl lg:text-7xl">
                <p className="bg-clip-text text-transparent drop-shadow-2xl bg-gradient-to-b from-white/80 to-white/20">
                    Gradients in Motion
                </p>
            </div>
        </BackgroundGradientAnimation>
    );
}
