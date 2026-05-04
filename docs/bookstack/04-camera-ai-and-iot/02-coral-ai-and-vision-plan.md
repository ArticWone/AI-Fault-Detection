# Coral AI and Vision Plan

## Current Coral Status

- Linux sees one Coral Edge TPU PCIe function: `1ac1:089a`.
- Device node: `/dev/apex_0`.
- Visible accelerator capacity: one TPU, about 4 TOPS.
- The dual card may physically contain two TPU chips, but this host/slot currently exposes only one.

## Use Coral For

- Fast local image classification/detection.
- Bad pack / missing product / jam candidate detection.
- Low-latency camera inference on selected frames.

## Do Not Use Coral For

- Chatbot/LMM reasoning.
- Large language models.
- Documentation search by itself.

## Recommended Architecture

Use Coral as the local vision accelerator, BookStack as the living manual, and a separate chatbot/reasoning layer later that can read logs, images, and docs.
