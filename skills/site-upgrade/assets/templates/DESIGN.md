---
version: alpha
name: <site>-design-system
description: <one sentence: the brand's visual world and its signature, as built>

colors:
  ground: "<#hex>"          # ~60% of the surface
  ground-alt: "<#hex>"      # the alternate section ground (dark or light)
  ink: "<#hex>"             # body text on ground
  ink-muted: "<#hex>"       # secondary text; tinted, never plain grey
  brand: "<#hex>"           # ~30%: support fields, the brand's own color
  accent: "<#hex>"          # ~10%: the primary action only
  signal: "<#hex>"          # one job only (e.g. data, or problems)
  on-brand: "<#hex>"

typography:
  display:
    fontFamily: "<Display face>, <fallbacks>"
    fontSize: <px or clamp()>
    fontWeight: <n>
    lineHeight: <n>
    letterSpacing: <em>
  heading:
    fontFamily: "<face>"
    fontSize: <px>
    fontWeight: <n>
    lineHeight: <n>
  body:
    fontFamily: "<Body face>, <fallbacks>"
    fontSize: 16px
    lineHeight: 1.55
  caption:
    fontFamily: "<face>"
    fontSize: 13px
    lineHeight: 1.4

spacing:
  section-y: <px, desktop>
  section-y-phone: <px>
  gutter: <px>
  container: <px>

rounded:
  control: <px or 9999px>
  card: <px>
  media: <px>
---

## Overview

<Two or three sentences: what the site is, the idea sentence, and the signature device. What someone should recognize with the logo covered.>

## Colors

<Each token's role and proportion. Where the accent may appear and where it may not. Which sections are dark and which light, and why.>

## Typography

<Roles, the scale (two or three sizes doing the visible work), tracking and leading. Where the accent face appears, and why it is earned.>

## Layout

<The grid, margins, section rhythm, the shared left edges. How the phone layout differs, not just shrinks.>

## Elevation and depth

<Tone steps between surfaces; which elements float and get a shadow; layered depth in the hero.>

## Components

<Navbar (and how it adapts to dark and light sections), buttons, the primary call to action, cards or tiles, forms, the footer. States: hover, focus, loading, error, empty.>

## Signature moments

<Each one: what happens, where, how it behaves with reduced motion, and the files that implement it.>

## Brand exceptions

<Devices that would read as generated elsewhere but are earned here, each with the brand material or owner decision behind it.>

## Do's and don'ts

### Do
- <…>

### Don't
- <…>

## Responsive behavior

| Width | What changes |
| --- | --- |
| ≥ 1440 | <…> |
| 1024–1439 | <…> |
| 768–1023 | <…> |
| < 768 | <…> |

## Iteration guide

1. Work on one component or section at a time.
2. Reference tokens by name (`{colors.accent}`), never raw values.
3. Keep the signature moments; extend the system before inventing a new device.
4. Update this file when the system changes.
