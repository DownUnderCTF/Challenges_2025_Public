// this original code is so cursed....
// i am just whacking stuff everywhere...

{
    const {
        requestAnimationFrame
    } = globalThis;
    const {
        alert
    } = globalThis;
    HTMLButtonElement.prototype.click = () => {
        alert(
            "Haha, lol try hard why u JavaScript >:D",
        );
    };
    HTMLButtonElement.prototype.focus = () => {
        alert(
            "monkeeeyeyeyeyeyeyeeyyeeyyeyey",
        );
    };
    Object.freeze(HTMLButtonElement);
    Object.freeze(HTMLButtonElement.prototype);
    const ready = () => {
        const button = document.getElementById("item");
        button.focus = null;
    //     button.style = `
    //   position: fixed;
	//     top: 200px;
	//     left: 200px;
	//     width: 300px;
    // 	height: 300px;
	//     border-radius: 8px;
    //   background-color:red;
    //   color: white;
	//     font-family: trebuchet MS;
	//     font-size: 20px;
	//     border: none;
	//     box-shadow: 4px 4px 0px rgb(82, 0, 114);
    //   user-select:none;`;
        button.onmousedown = function() {
            button.style.boxShadow = "3px 2px 1px rgb(80, 0, 110)";
        };
        button.onmouseup = function() {
            button.style.boxShadow = "4px 4px 0px rgb(82, 0, 114)";
            button.style.animation = "wobble 1s";
        };

        let x = 0;
        let y = 0;
        let button_x = 200;
        let button_y = 200;

        const runAway = (e) => {
            x = e.pageX;
            y = e.pageY;
            button.style.left = (x + 20) + "px";
            button.style.top = (y + 20) + "px";
        };
        const onClick = (e) => {
            // I honestly have no idea what on earth this code is doing
        //     if (e.isTrusted && e instanceof MouseEvent) {
        //         alert("You got me!");
        //     } else if (e.screenX === 0 && e.screenY === 0) {
        //         alert(
        //             "congrats monkes this code been coppied",
        //         );
        //     } else {
        //         alert("HaHa, nice try >:D");
        //     }
        };
        const onLeave = () => {

        };
        const onEnter = () => {

        };
        const oncontext = (e) => false;
        button.onclick = onClick;
        document.onmousemove = runAway;
        window.onmouseout = onLeave;
        window.onmouseover = onEnter;
        window.oncontextmenu = oncontext;
        const loop = () => {
            if (button.onclick !== onClick) {
                button.onclick = onClick;
            }
            if (document.onmousemove !== runAway) {
                document.onmousemove = runAway;
            }
            if (window.oncontextmenu !== oncontext) {
                window.oncontextmenu = oncontext;
            }
            if (window.onmouseout !== onLeave) {
                window.onmouseout = onLeave;
            }
            if (window.onmouseover !== onEnter) {
                window.onmouseover = onEnter;
            }
            if (
                !button.hasAttribute("tabindex") ||
                button.getAttribute("tabindex") !== "-1"
            ) {
                button.setAttribute("tabindex", "-1");
            }
            if (button.style.position !== "fixed") {
                button.style.position = "fixed";
            }
            if (button.style.width !== "200px" || button.style.height !== "100px") {
                button.style.width = "200px";
                button.style.height = "100px";
            }
            requestAnimationFrame(loop);
        };
        loop();
        //Ha, nice try guys ;)
        globalThis.alert = (message) => {
            alert(
                "glory to malta",
            );
        };
    };
    if (document.readyState !== "loading") {
        ready();
    } else {
        window.addEventListener("DOMContentLoaded", ready);
    }
}
