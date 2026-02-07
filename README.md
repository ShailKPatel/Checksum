# Checksum Verifier

A visual, educational tool designed to demonstrate the **Internet Checksum** (RFC 1071) algorithm and error detection principles for Computer Networks courses.

## Overview

This application simulates a sender-receiver network model to visualize:
1.  **Data to Binary Conversion**
2.  **Checksum Generation** (16-bit One's Complement Sum)
3.  **Data Transmission** (with optional corruption simulation)
4.  **Checksum Verification** at the receiver end.

## Features

-   **Step-by-Step Visualization**: See every binary addition, carry wrap, and inversion.
-   **Manual Corruption Simulation**: Edit the packet payload or checksum *before* it is sent to the "wire" to see how verification fails.
-   **Dual-View Interface**: Separate Sender and Receiver pages to simulate distinct network endpoints.

## Tech Stack

-   **Backend**: Python 3.9+, FastAPI
-   **Templating**: Jinja2
-   **Frontend**: HTML5, CSS3 (Custom styling, no external frameworks like Bootstrap or Tailwind)
-   **Fonts**: Google Fonts ("Press Start 2P")
-   **Server**: Uvicorn

## How to Run

1.  **Requirements**: Python 3.x, `fastapi`, `uvicorn`, `python-multipart`.
2.  **Start**:
    -   run: `python -m uvicorn main:app --reload`
3.  **Access**:
    -   Sender: `http://127.0.0.1:8000/sender`
    -   Receiver: `http://127.0.0.1:8000/receiver`

## Educational Goals

-   Understand why checksums are needed.
-   Visualize how 1's complement arithmetic calculates a checksum.
-   Observe the result of bit-flipping (corruption) on the final verification sum.
