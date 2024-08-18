; create_ball_table
;
; Creates ballTable.ini and extracts the default gooballIds table into it.
;
; Input: rbx - SDL2Storage* storage
; Result: rax - bool success (1 if success, 0 if error)
; Clobbers: ?
create_ball_table:
    push rbp
    push r12
    push rdi
    push r13
    
    mov rbp, rsp
    sub rsp, 0x28 + 0x80 + 0x20
    
    mov r12, qword [rbx] ; r12 = storage->vtable
    
    ; SDL2Storage::FileOpen (vtable[2])
    mov rcx, rbx ; this
    lea rdx, [rel ballTablePath] ; filePath
    mov r8, 0x22 ; flags (0x22 : "w+b")
    lea r9, [rbp-0x10] ; out_fileHandle
    call qword [r12+0x10]
    
    ; if (result != 0) goto create_ball_table_failure
    test rax, rax
    jne create_ball_table_failure
    
    
    ; FileOpen succeded
    mov rdi, qword [rbp-0x10] ; rdi = fileHandle
    
    ; write header
    ; SDL2Storage::FileWrite (vtable[4])
    mov rcx, rbx ; this
    mov rdx, rdi ; fileHandle
    lea r8, [rel ballTableHeader] ; content
    mov r9, ballTableHeaderLen ; size
    call qword [r12+0x20]
    
    
    ; loop: print all default gooball ids
    mov r13, 0 ; r13 = int i
create_ball_table_loop_start:
    lea rcx, [rel load_config_hook-0xF94B50] ; gooballIds
    mov rcx, [rcx + r13 * 8]
    mov [rsp+0x20], rcx
    
    ; snprintf
    lea rcx, [rbp-0x90] ; dst
    mov rdx, 0x80 ; = 128, n
    lea r8, [rel ballTableLineFormat] ; format
    mov r9, r13 ; var arg 0
    call load_config_hook-0x1A62720
    
    ; SDL2Storage::FileWrite (vtable[4])
    mov rcx, rbx ; this
    mov rdx, rdi ; fileHandle
    lea r8, [rbp-0x90] ; content
    mov r9, rax ; size
    call qword [r12+0x20]
    
    add r13, 1
    cmp r13, baseGooballCount
    jl create_ball_table_loop_start
    
    
    ; SDL2Storage::FileClose (vtable[5])
    mov rcx, rbx ; this
    mov rdx, rdi ; fileHandle
    call qword [r12+0x28]
    
    mov rax, 1 ; 1 for success
    
create_ball_table_merge:
    add rsp, 0x28 + 0x80 + 0x20
    
    pop r13
    pop rdi
    pop r12
    pop rbp
    ret
    
create_ball_table_failure:
    ; Show error message that ballTable.ini could not be created
    ; SDL_ShowSimpleMessageBox
    mov ecx, 0x10
    lea rdx, [rel msgTitle]
    lea r8, [rel msgBallTableCreateErr]
    xor r9, r9
    call load_config_hook-0x1AADD91
    
    xor rax, rax ; 0 for error
    jmp create_ball_table_merge

; constants
msgBallTableCreateErr db \
    "Failed to create ballTable.ini file. Make sure the game directory is not ",\
    "inside C:\Program Files or any other place that requires administrator permissions.", 0Ah, 0Ah,\
    "Continuing with default settings.", 00h
    
ballTableHeader db \
    "; This table defines all Gooball typeEnums", 0Dh, 0Ah, \
    "; Extend this list to add your own gooballs.", 0Dh, 0Ah, \
    "; ", 0Dh, 0Ah, \
    "; Generated by FistyLoader 0.1", 0Dh, 0Ah, 0Dh, 0Ah, 00h
ballTableHeaderLen equ $-ballTableHeader - 1
ballTableLineFormat db "%d=%s", 0Dh, 0Ah, 00h
