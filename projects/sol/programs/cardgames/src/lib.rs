use anchor_lang::prelude::*;

declare_id!("HUmGzNGXPcvw7vrym2whekRPr1JCAbnM1eEG53jXkjhB");

#[program]
pub mod cardgames {
    use super::*;

    pub fn initialize(ctx: Context<Initialize>) -> Result<()> {
        msg!("Greetings from: {:?}", ctx.program_id);
        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize {}
