

from torch.cuda.amp import GradScaler

scaler = GradScaler()

with autocast():
    outputs = model(inputs)
    loss = loss_fn(outputs, targets)

scaler.scale(loss).backward()
scaler.step(optimizer)
scaler.update()
