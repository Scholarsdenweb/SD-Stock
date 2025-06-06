// get shirt and diary checkbox and make size dropdown
const itemCheckboxes = document.getElementsByName('item')
const shirtSizeContainer = document.getElementById('id_item').firstChild
const diarySizeContainer = document.getElementById('id_item')

console.log(shirtSizeContainer)

itemCheckboxes.forEach(checkbox => {
    checkbox.addEventListener('change', (e) => {
        if(e.target.checked){
            if(e.target.value == 'shirt' || e.target.value == 't-shrit'){
                const sizes = ['s', 'm', 'l', 'xl', 'xxl']
                sizeSelector = createOptions(sizes)
                sizeSelector.id = 'id_shirt_size'
                

                e.target.parentNode.parentNode.appendChild(sizeSelector)
            }

            if(e.target.value.toLowerCase() == 'diary'){
                const sizes = ['small', 'big']
                sizeSelector = createOptions(sizes)
                sizeSelector.id = 'id_diary_size'
                e.target.parentNode.parentNode.appendChild(sizeSelector)
            }
        }
        else{

            const shirtSizeSelector = document.getElementById('id_shirt_size')
            const diarySizeSelector = document.getElementById('id_diary_size')

            if(shirtSizeSelector){

                e.target.parentNode.parentNode.removeChild(shirtSizeSelector)
            }
            if(diarySizeSelector){
                e.target.parentNode.parentNode.removeChild(diarySizeSelector)
            }

        }

        
    })
})

function createOptions(sizes){
    let selectElement = document.createElement('select')
    
    sizes.forEach(size => {
        const option = document.createElement('option')
        option.value = size
        option.innerHTML = size.toUpperCase()
        selectElement.appendChild(option)
    })

    return selectElement

}

