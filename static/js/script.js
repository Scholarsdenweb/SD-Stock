

document.body.addEventListener('htmx:afterSwap', () => {
    const returnForm = document.querySelector('#returnform')
    const listWraper = document.querySelector('.list-wraper')
    const refreshBtn = document.querySelector('#refreshbtn')

    refreshBtn.addEventListener('click', () => {
        returnForm.reset()
    })
})
