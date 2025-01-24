import os
#_data_root = os.environ.get('DATA_ROOT')
#_data_root = 'D:/DeskTop/seg/BPR-main/BPR-main/thresh_0_25_ps_64_pd_0'
_data_root = r'D:\DeskTop\seg\BPR-main\BPR-main\tools\patches\giou'
del os

_base_ = [
    '../_base_/default_runtime.py',
    '../_base_/schedules/schedule_160k.py'
]
train_cfg = dict()
test_cfg = dict(mode='whole')
# model settings
norm_cfg = dict(type='BN', requires_grad=True)
model = dict(
    type='EncoderDecoderRefine',
    train_cfg=train_cfg,
    test_cfg=test_cfg,
    #pretrained='open-mmlab://msra/hrnetv2_w18_small',
    backbone=dict(
        type='HRNet',
        norm_cfg=norm_cfg,
        norm_eval=False,
        extra=dict(
            stage1=dict(
                num_modules=1,
                num_branches=1,
                block='BOTTLENECK',
                num_blocks=(2, ),
                num_channels=(64, )),
            stage2=dict(
                num_modules=1,
                num_branches=2,
                block='BASIC',
                num_blocks=(2, 2),
                num_channels=(18, 36)),
            stage3=dict(
                num_modules=3,
                num_branches=3,
                block='BASIC',
                num_blocks=(2, 2, 2),
                num_channels=(18, 36, 72)),
            stage4=dict(
                num_modules=3,
                num_branches=4,
                block='BASIC',
                num_blocks=(2, 2, 2, 2),
                num_channels=(18, 36, 72, 144),
            downsample=dict(
                in_channels_dict=(18, 36, 72, 144),  # input channels for the downsample layer
                out_channels=64,  # output channels for the downsample layer
                kernel_size=3,
                stride=2,
                padding=1,
                bias=False
            )
            ))),
    decode_head=dict(
        type='FCNHead',
        in_channels=[18, 18, 18, 18, 18],
        in_index=(0, 1, 2, 3, 4),
        channels=sum([18, 18, 18, 18, 18]),
        input_transform='resize_concat',
        kernel_size=1,
        num_convs=1,
        concat_input=False,
        dropout_ratio=-1,
        num_classes=2,
        norm_cfg=norm_cfg,
        align_corners=False,
        loss_decode=dict(
            type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0)))

# dataset settings
dataset_type = 'RefineDataset'
data_root = _data_root
img_norm_cfg = dict(
    mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True)
crop_size = (128, 128)
train_pipeline = [
    dict(type='LoadImageFromFile'),
    dict(type='LoadAnnotations'),
    dict(type='LoadCoarseMask'),
    dict(type='Resize', img_scale=crop_size, ratio_range=(1.0, 1.0)),
    dict(type='RandomFlip', flip_ratio=0.5),
    dict(type='PhotoMetricDistortion'),
    dict(type='Normalize', **img_norm_cfg),
    dict(type='Pad', size=crop_size),
    dict(type='DefaultFormatBundle'),
    dict(type='Collect', keys=['img', 'gt_semantic_seg', 'coarse_mask']),
]
test_pipeline = [
    dict(type='LoadImageFromFile'),

    dict(type='LoadAnnotations'),
    dict(type='LoadCoarseMask'),
    dict(
        type='MultiScaleFlipAug',
        img_scale=crop_size,
        flip=False,
        transforms=[
            dict(type='Resize', img_scale=crop_size, keep_ratio=True),
            dict(type='RandomFlip'),
            dict(type='Normalize', **img_norm_cfg),
            dict(type='ImageToTensor', keys=['img']),
            dict(type='Collect', keys=['img', 'coarse_mask']),
        ])
]


data = dict(
    samples_per_gpu=8,
    workers_per_gpu=1,
    train=dict(
        type=dataset_type,
        data_root=data_root,
        img_dir='img_dir/train',
        mask_dir='mask_dir/train',
        ann_dir='ann_dir/train',
        pipeline=train_pipeline),
    val=dict(
        type=dataset_type,
        data_root=data_root,
        img_dir='img_dir/val',
        mask_dir='mask_dir/val',
        ann_dir='ann_dir/val',
        pipeline=test_pipeline),
    test=dict(
        type=dataset_type,
        data_root=data_root,
        img_dir='img_dir/val',
        mask_dir='mask_dir/val',
        ann_dir='ann_dir/val',
        pipeline=test_pipeline))
