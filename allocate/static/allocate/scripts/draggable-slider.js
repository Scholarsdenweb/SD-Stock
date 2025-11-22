const tabBox = document.querySelector(".tab-box");
arrowIcons = document.querySelectorAll(".arrows i");

let isDragging = false ;

console.log('draggable not working')
const handleIcon = (scrollValue) => {
    let maxScrollWidth = tabBox.scrollWidth - tabBox.clientWidth;
    arrowIcons[0].parentElement.style.display = scrollValue <= 0 ? "none" : "flex";
    arrowIcons[1].parentElement.style.display = maxScrollWidth - scrollValue <= 1 ? "none" : "flex";
}

arrowIcons.forEach(icon => {
    icon.addEventListener("click", () => {
        let scrollWidth = tabBox.scrollLeft += icon.id === 'left' ? -340 : 340;
        handleIcon(scrollWidth)
    })
})

const dragging = (e) => {
    if(!isDragging) return; // if isDragging is false return from here
    tabBox.classList.add("dragging");
    tabBox.scrollLeft -= e.movementX; // decrease the value of scrollLeft by x axis movement of mouse
    handleIcon(tabBox.scrollLeft)
}

const dragStop = () => {
    isDragging = false;
    if(tabBox){
        tabBox.classList.remove("dragging");
    }
}

if(tabBox){
    tabBox.addEventListener("mousedown", () => isDragging = true);
    tabBox.addEventListener("mousemove", dragging);
}

document.addEventListener("mouseup", dragStop);

