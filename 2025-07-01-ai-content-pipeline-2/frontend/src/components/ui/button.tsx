import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import type * as React from "react";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-1.5 whitespace-nowrap font-medium transition-all duration-150 cubic-bezier(0.25, 0.46, 0.45, 0.94) disabled:pointer-events-none disabled:opacity-40 [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 outline-none macos-focus active:scale-95 active:brightness-95",
  {
    variants: {
      variant: {
        default:
          "bg-primary text-primary-foreground hover:bg-primary/90 active:bg-primary/80 macos-text-body font-medium border border-primary/20 shadow-[0_1px_3px_rgba(0,0,0,0.1),inset_0_1px_0_rgba(255,255,255,0.1)]",
        destructive:
          "bg-destructive text-white hover:bg-destructive/90 active:bg-destructive/80 macos-text-body font-medium border border-destructive/20 shadow-[0_1px_3px_rgba(0,0,0,0.1),inset_0_1px_0_rgba(255,255,255,0.1)]",
        outline:
          "border border-border/60 macos-material-content hover:border-border active:border-border/80 macos-text-body font-medium backdrop-blur-md",
        secondary:
          "macos-material-sidebar text-secondary-foreground hover:opacity-80 active:opacity-70 macos-text-body font-medium border border-white/10",
        ghost:
          "hover:macos-material-content hover:backdrop-blur-md active:bg-accent/70 macos-text-body font-medium",
        link: "text-primary underline-offset-4 hover:underline bg-transparent macos-text-body font-medium",
      },
      size: {
        default: "h-8 px-4 rounded-[6px] macos-text-body",
        sm: "h-7 px-3 rounded-[5px] macos-text-callout",
        lg: "h-9 px-6 rounded-[7px] macos-text-body",
        icon: "h-8 w-8 rounded-[6px]",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);

function Button({
  className,
  variant,
  size,
  asChild = false,
  ...props
}: React.ComponentProps<"button"> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean;
  }) {
  const Comp = asChild ? Slot : "button";

  return (
    <Comp
      data-slot="button"
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  );
}

export { Button, buttonVariants };
