const magnifier = document.getElementById("magnifier");
const signature = document.getElementById("signature");

function startScan() {
    const rect = signature.getBoundingClientRect();
    const parentRect = signature.parentElement.getBoundingClientRect();

    const areaLeft = rect.left - parentRect.left;
    const areaTop = rect.top - parentRect.top;
    const areaWidth = rect.width;
    const areaHeight = rect.height;

    const glassSize = 180;
    const padding = 50;

    // UI Layering
    magnifier.style.pointerEvents = "none";
    magnifier.style.opacity = 1;
    magnifier.style.position = "absolute";
    magnifier.style.left = "0px";
    magnifier.style.top = "0px";
    magnifier.style.willChange = "transform";

    // Professional Waypoints
    const path = [
        { x: areaLeft + padding, y: areaTop + padding },
        { x: areaLeft + areaWidth - glassSize - padding, y: areaTop + (areaHeight - glassSize) / 2 },
        { x: areaLeft + (areaWidth - glassSize) / 2, y: areaTop + (areaHeight - glassSize) / 2 },
        { x: areaLeft + padding + 20, y: areaTop + areaHeight - glassSize - padding },
        { x: areaLeft + (areaWidth - glassSize) / 2, y: areaTop + (areaHeight - glassSize) / 2 }
    ];

    let segment = 0;
    let tStart = performance.now();

    function animateSegment(time) {
        // ADJUSTED TIMES: Much slower movement (7-8 seconds)
        // This ensures the "inspection" phase is the focus.
        const durations = [8000, 7000, 8000, 7000];
        const duration = durations[segment];

        let t = (time - tStart) / duration;
        if (t > 1) t = 1;

        // "Smooth Glide" Easing: Removes the heavy "clunk" at the waypoints.
        // It slows down just enough to signal a change in direction, then proceeds.
        let easedT = t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;

        const start = path[segment];
        const end = path[segment + 1];

        const midX = (start.x + end.x) / 2;
        const midY = (start.y + end.y) / 2 - 15;

        // Bezier calculation for the signature curve
        const x = (1 - easedT) * (1 - easedT) * start.x + 2 * (1 - easedT) * easedT * midX + easedT * easedT * end.x;
        const y = (1 - easedT) * (1 - easedT) * start.y + 2 * (1 - easedT) * easedT * midY + easedT * easedT * end.y;

        // translate3d eliminates sub-pixel vibration
        magnifier.style.transform = `translate3d(${x}px, ${y}px, 100px)`;

        if (t < 1) {
            requestAnimationFrame(animateSegment);
        } else {
            segment++;
            if (segment < path.length - 1) {
                // NO DELAY: Immediate transition to the next segment
                tStart = performance.now();
                requestAnimationFrame(animateSegment);
            } else {
                // Final verification pause
                setTimeout(showResultInsideLens, 1000);
            }
        }
    }

    requestAnimationFrame(animateSegment);
}


function showResultInsideLens() {
    const lens = magnifier.querySelector(".lens");
    const isMatch = Math.random() > 0.3;

    const message = document.createElement("div");

    message.classList.add("scan-result");
    message.classList.add(isMatch ? "match" : "no-match");

    message.innerHTML = isMatch ? "MATCH FOUND" : "NO MATCH FOUND";

    lens.appendChild(message);

    setTimeout(() => {
        message.style.opacity = "1";
    }, 100);
}


setTimeout(startScan, 1500);