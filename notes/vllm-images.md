## sending images to a vllm model

const base64ImageMessage = new HumanMessage({
    content: [{
            type: 'text',
            text: `${input}`,
        },{
            type: 'image_url',
            image_url: fileBase64,
        },
    ],
});