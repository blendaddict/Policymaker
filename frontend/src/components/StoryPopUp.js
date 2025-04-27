import { Dialog, DialogTitle, DialogContent, Typography, IconButton } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

export default function StoryPopup({ open, onClose, story }) {
  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>
        Blob Story
        <IconButton
          aria-label="close"
          onClick={onClose}
          sx={{ position: 'absolute', right: 8, top: 8, width:"1vh", height:"1vh"}}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      <DialogContent dividers  style={{minWidth:"20vw", minHeight:"30vh"}}>
        <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>
          {story}
        </Typography>
      </DialogContent>
    </Dialog>
  );
};
