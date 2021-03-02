let g:quickrun_config = {
            \   "_": {
            \       "outputter/buffer/close_on_empty": 1
            \   }
            \}

set foldmethod=indent
set foldlevel=1

nnoremap <F5> :!python main.py<CR>
nnoremap <F7> :!python %<CR>

au BufWrite *.py :Autoformat
au BufWrite *.exrc :Autoformat

let g:formatters_python = ['black']
