const itemName = document.getElementById('id_name')
const itemSizeSelect = document.getElementById('id_size')
// const originalSize = itemSizeSelect.innerHTML
itemSizeSelect.innerHTML = ''

// remove the alter box ater 5 seconds
$(document).ready(function(){
   $('.alert').delay(5000).fadeOut('slow')
})


itemName.addEventListener('blur', (e) => {
    if(e.target.value.toLowerCase().includes("shirt")){
        itemSizeSelect.innerHTML = ''
        itemSizeSelect.disabled = false
        const sizes = ['s', 'm', 'l', 'xl', 'xxl']
        createOptions(sizes)
    }
    else if(e.target.value.toLowerCase() == 'diary'){
        itemSizeSelect.innerHTML = ''
        itemSizeSelect.disabled = false
        const sizes = ['small', 'big']
        createOptions(sizes)
    }

    else { 
        itemSizeSelect.innerHTML = '' 
        itemSizeSelect.disabled = true
    }
       

    
})


function createOptions(sizes){
    
    sizes.forEach(size => {
        const option = document.createElement('option')
        option.value = size
        option.innerHTML = size.toUpperCase()
        itemSizeSelect.appendChild(option)
    })

}


console.log("Hello")