# Wan2.2 Image-to-Video Prompting Guide

## Core Principle

The image already defines the subject, scene, and style. Your prompt should describe **motion and camera movement**, not what's in the frame.

## Prompt Formula

**Prompt = Motion Description + Camera Movement**

Aim for **80–120 words**. Shorter is too vague, longer overwhelms the model.

## Priority Order

1. **Subject identity** — what's in frame, defining characteristics
2. **Motion hierarchy** — what moves fast, what moves slow, what stays still
3. **Camera behavior** — how we're "filming" the motion
4. **Style and atmosphere** — lighting, mood, artistic style

## Motion Tips

- Use specific verbs: "swings", "stumbles", "drifts" not "moves"
- Control intensity with adjectives: "forcefully", "gently", "slowly"
- Define primary vs secondary motion — everything moving equally looks noisy
- Keep to **one continuous scene** per generation

## Camera Phrases

| Phrase | Effect |
|--------|--------|
| `fixed lens` | Static camera, no movement |
| `camera slowly pushes forward` | Dolly in |
| `camera pans left` | Horizontal pan |
| `slight camera shake` | Handheld feel |
| `tracking shot following subject` | Camera follows action |
| `close-up` | Tight framing |

## Example Prompts

### Pillow Fight (3D Animated)
> Bear swings pillow forcefully at raccoon, feathers explode outward and drift slowly through the air, raccoon stumbles backward clutching a glowing pillow, slight camera shake, warm cozy room lighting, 3D animated Pixar style, fixed focal length, soft shadows, scattered feathers settling on the floor

### Dramatic Portrait
> Subject turns head slowly toward camera, wind catches hair, eyes narrow with determination, cinematic tone, soft key light from camera left at 45 degrees, warm rim light from behind, bokeh background, subtle film grain

### Product Shot
> Product rotates slowly on pedestal, light reflections glide across surface, clean studio environment, softbox from above, subtle fill from below, crisp reflections, no camera movement

## Known Limitations

- **Hands**: Static hands work fine, moving hands artifact ~40% of the time
- **Multiple characters interacting**: ~65% artifact rate — model struggles with interaction physics
- **Fast motion**: Whip pans and rapid movement cause smearing and doubling
- **Scene transitions**: Don't pack multiple scenes into one prompt

## Iteration Strategy

- Start with simple single-motion prompts before combining effects
- Adjust one element at a time (motion, camera, lighting)
- Use short 4-second drafts to test before 8-second final renders
- Track prompt variants — small wording changes can produce very different results
